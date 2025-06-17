from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import pytesseract
from pytesseract import Output
from PIL import Image, ImageDraw, ImageFont
import sys
import matplotlib.pyplot as plt
import subprocess
import os
from groq import Groq
import traceback
import numpy as np
import cv2 

from flask import send_from_directory

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)

client = Groq(api_key="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")

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Cargar BD una vez
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Une el directorio base con el nombre de tu archivo Excel
bd_path = os.path.join(BASE_DIR, 'BD.xlsx')
if not os.path.exists(bd_path):
    raise FileNotFoundError("No se encontró BD.xlsx")

df = pd.read_excel(bd_path)
df["Cedula"] = df["Cedula"].astype(str).str.replace(".0", "", regex=False)
df["Clave"] = df["Clave"].astype(str).str.replace(".0", "", regex=False)


@app.route('/Infografias/<filename>')
def serve_infografia(filename):
    return send_from_directory('Infografias', filename)


def reemplazar_texto(input_image_path, output_image_path, texts_to_replace, new_texts, text_styles):
    # Leer la imagen de entrada
    image = cv2.imread(input_image_path)

    if image is None:
        print("Error al abrir la imagen.")
        return

    # Convertir la imagen a escala de grises para mejorar la detección de texto
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detectar texto en la imagen usando Tesseract
    data = pytesseract.image_to_data(gray_image, output_type=Output.DICT)

    # Crear una máscara para el inpainting
    mask = np.zeros(gray_image.shape, dtype=np.uint8)

    for text_to_replace, new_text in zip(texts_to_replace, new_texts):
        for i in range(len(data['text'])):
            detected_text = data['text'][i].strip()

            if detected_text and text_to_replace in detected_text:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                mask[y:y + h, x:x + w] = 255
                print(f'Texto "{text_to_replace}" encontrado y marcado para reemplazo en la imagen.')

    modified_image = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)

    pil_image = Image.fromarray(cv2.cvtColor(modified_image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)

    for text_to_replace, new_text, style in zip(texts_to_replace, new_texts, text_styles):
        for i in range(len(data['text'])):
            detected_text = data['text'][i].strip()

            if detected_text and text_to_replace in detected_text:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

                # Ajustar el tamaño de la fuente
                font_size = style.get('font_size', h)  # Usa el definido o la altura del texto detectado
                font = ImageFont.truetype(style['font_path'], font_size)

                # Obtener el tamaño del texto
                bbox = draw.textbbox((0, 0), new_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # Calcular la posición del texto centrado
                text_x = x + (w - text_width) // 2
                text_y = y + (h - text_height) // 2

                # Dibujar fondo rectangular antes del texto
                padding = style.get('padding', 15)
                background_color = style.get('background_color', (255, 255, 255))  # Fondo blanco por defecto

                # Coordenadas del fondo
                rect_x0 = text_x - padding
                rect_y0 = text_y - padding
                rect_x1 = text_x + text_width + padding
                rect_y1 = text_y + text_height + padding

                # Dibujar rectángulo
                draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=background_color)

                # Dibujar el texto en la imagen
                draw.text((text_x, text_y-10), new_text, font=font, fill=style['color'])
                print(
                    f'Texto "{text_to_replace}" reemplazado por "{new_text}" en la imagen en la posición {(text_x, text_y)}.')
    

    # Convertir de PIL a OpenCV (BGR)
    modified_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Guardar imagen
    cv2.imwrite(output_image_path, modified_image)

    # Abrir con la aplicación predeterminada (Fotos en Windows)
    os.startfile(output_image_path)

    return (output_image_path)


# Ruta de prueba simple
@app.get("/")
def inicio():
    return "✅ Servidor Flask funcionando"

# Ruta de login
@app.post("/login")
def login():
    try:
        data = request.get_json(force=True)
        cedula = data.get("cedula", "")
        clave  = data.get("clave", "")
        print(f"📥 Login recibido → cedula: '{cedula}', clave: '{clave}'")
    except Exception:
        return jsonify({"status":"error","detail":"JSON mal formado"}), 400

    cliente = df[(df["Cedula"]==cedula)&(df["Clave"]==clave)]
    print(cliente)
    if not cliente.empty:
        nombre = cliente.iloc[0]["Nombre"]
        return jsonify({"status":"ok","nombre":nombre})
    else:
        return jsonify({"status":"error","detail":"Credenciales incorrectas"}), 401

# Ruta para generar infografía
@app.post("/infografia/<cedula>")
def generar_infografia(cedula):
    try:
        resultado = subprocess.run(["python", "imagen.py", cedula], capture_output=True, text=True)
        return jsonify({"status": "ok", "output": resultado.stdout})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.post("/generar-imagen")
def endpoint_generar_imagen():
    data = request.get_json()
    cedula = data.get('cedula')

    if not cedula:
        return jsonify({"error": "Cédula no proporcionada"}), 400

    bd_path2 = os.path.join(BASE_DIR, 'BD.xlsx')
    input_image_path = os.path.join(BASE_DIR, 'Infografias', 'Infografia.png')
    output_image_path = os.path.join(BASE_DIR, 'Infografias', 'Infografia_Personalizada.png')

    # Leer el Excel
    df = pd.read_excel(bd_path2, dtype={'Cedula': str})
    df['Cedula'] = df['Cedula'].astype(str).str.strip()

    # Buscar la cédula
    cedula = str(cedula).strip()
    fila = df[df['Cedula'] == cedula]

    print(fila)

    # Verificar existencia de la imagen base
    print("¿Existe la imagen?", os.path.exists(input_image_path))

    # Obtener datos de la fila
    nombre = fila.iloc[0]['Nombre']
    numero_cuota=fila.iloc[0]['Numero de cuota']
    ultimos_digitos=fila.iloc[0]['Digitos finales tarjeta']
    monto=fila.iloc[0]['Monto Libre Inversion']
    plazo=fila.iloc[0]['Plazo en meses']
    t_efectiva_anual=fila.iloc[0]['EA']
    t_efectiva_mensual=fila.iloc[0]['EM']

    cuota_mensual=fila.iloc[0]['Cuota mensual']
    cuota_capital=fila.iloc[0]['Cuota capital']
    cuota_seguro=fila.iloc[0]['Cuota seguro']
    numero_cuota_2=fila.iloc[0]['Numero de cuota 2']
    dia_last_pago=fila.iloc[0]['Dia']
    mes_last_pago=fila.iloc[0]['Mes']
    ano_last_pago=fila.iloc[0]['Año']
    fecha_last_pago=fila.iloc[0]['Ultimo pago']
    pago_intereses=fila.iloc[0]['Pago intereses']

    def convertir_string(valor):
        if isinstance(valor, float) and valor.is_integer():
            return str(int(valor))
        return str(valor)

    # Texto a buscar y reemplazar
    texts_to_replace = ['XXXXX',"YYY", 'NNN','ZZ',"WW","AA","MMM","TTTTTT","BBBBBBB","DDDDDDD","LLL","EEEEEEEEEE","HHHHH"]
    new_texts = ["¡Hola "+nombre+"!", 
                convertir_string(numero_cuota)
                ,convertir_string(ultimos_digitos)
                ,convertir_string(monto)
                ,convertir_string(plazo)
                ,convertir_string(t_efectiva_anual)+"%"
                ,convertir_string(t_efectiva_mensual)+"%"
                ,"$"+convertir_string(cuota_mensual)
                ,"$"+convertir_string(cuota_capital)
                ,"$"+convertir_string(cuota_seguro)
                ,convertir_string(numero_cuota_2)
                #  ,convertir_string(dia_last_pago)+"/"
                #  ,convertir_string(mes_last_pago)+"/"
                ,convertir_string(fecha_last_pago)
                ,"$"+convertir_string(pago_intereses)]


    roboto_black = os.path.join(BASE_DIR, 'Tipografias', 'Roboto-Black.ttf')
    roboto_bold = os.path.join(BASE_DIR, 'Tipografias', 'Roboto-Bold.ttf')
    roboto_regular = os.path.join(BASE_DIR, 'Tipografias', 'Roboto-Regular.ttf')

    negro=(0,0,0)
    blanco=(255,255,255)
    rojo=(237,28,39) #ED1C27
    gris_claro=(240,240,240) #F0F0F0
    gris_oscuro=(217,217,217) #D9D9D9
    azul=(0,14,51) #000E33

    text_styles = [
        {'font_path': roboto_black, 'color': negro, 'font_size': 80, 'background_color': blanco,'padding':20}, #Nombre
        {'font_path': roboto_bold, 'color': negro, 'font_size': 70, 'background_color': blanco,'padding':20}, #Numero Cuota
        {'font_path': roboto_regular, 'color': blanco, 'font_size': 60, 'background_color': azul,'padding':20}, #Ultimos digitos
        {'font_path': roboto_black, 'color': blanco, 'font_size': 72, 'background_color': azul,'padding':20}, #Monto
        {'font_path': roboto_black, 'color': blanco, 'font_size': 72, 'background_color': azul,'padding':20}, #Plazo
        {'font_path': roboto_black, 'color': rojo, 'font_size': 96, 'background_color': gris_claro,'padding':50}, #EA
        {'font_path': roboto_black, 'color': rojo, 'font_size': 96, 'background_color': gris_claro,'padding':50}, #EM

        {'font_path': roboto_bold, 'color': blanco, 'font_size': 80, 'background_color': azul,'padding':28}, #Cuota mensual
        {'font_path': roboto_black, 'color': rojo, 'font_size': 80, 'background_color': gris_oscuro,'padding':30},#Cuota capital
        {'font_path': roboto_black, 'color': rojo, 'font_size': 80, 'background_color': gris_oscuro,'padding':30}, #Cuota seguro
        {'font_path': roboto_black, 'color': blanco, 'font_size': 72, 'background_color': azul,'padding':20}, #Num cuota 2
        # {'font_path': roboto_black, 'color': blanco, 'font_size': 96, 'background_color': azul,'padding':10}, #Dia
        # {'font_path': roboto_black, 'color': blanco, 'font_size': 96, 'background_color': azul,'padding':10}, #Mes
        {'font_path': roboto_black, 'color': blanco, 'font_size': 72, 'background_color': azul,'padding':10}, #Año
        {'font_path': roboto_black, 'color': blanco, 'font_size': 72, 'background_color': azul,'padding':25} #Pago interese
    ]

    resultado=reemplazar_texto(input_image_path, output_image_path, texts_to_replace, new_texts, text_styles)
    
    #return jsonify({"mensaje": resultado}), 200
    return jsonify({
        "imagen_url": "http://localhost:5000/Infografias/Infografia_Personalizada.png"
    }), 200


@app.post("/chat")
def chat():
    try:
        data = request.get_json(force=True)
        mensaje = data.get("mensaje", "")
        app.logger.info(f"📥 Mensaje recibid o en /chat: {mensaje}")

        palabras_clave = ["interés", "intereses", "crédito", "créditos",
                          "capital", "cuota", "cuotas"]
        tiene_clave = any(p in mensaje.lower() for p in palabras_clave)

        # Llamada al modelo
        respuesta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content":
                    "Eres un asesor bancario experto llamado Vivi, muy cordial, claro y que ayuda al usuario con ejemplos financieros."},
                {"role": "user", "content": mensaje}
            ]
        )

        content = respuesta.choices[0].message.content.strip()
        app.logger.info(f"✅ Respuesta del modelo: {content[:60]}...")

        if tiene_clave:
            return jsonify({
                "respuesta": "📊 Tengo un contenido para ti sobre este tema.",
                "mostrar_botones": True
            })
        else:
            return jsonify({
                "respuesta": content,
                "mostrar_botones": False
            })

    except Exception as e:
        # Imprime stack trace completo en la consola de Flask
        tb = traceback.format_exc()
        app.logger.error("❌ Error en /chat:\n" + tb)
        return jsonify({
            "respuesta": "Lo siento, ocurrió un error interno.",
            "mostrar_botones": False
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    

