import cv2
import os
import numpy as np
import pytesseract
from pytesseract import Output
from PIL import Image, ImageDraw, ImageFont
import sys
import matplotlib.pyplot as plt
import pandas as pd


from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory

app = Flask(__name__)

# Habilitar CORS correctamente
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})


# Ruta de Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



cedula_recuperada=1000953583

@app.route('/Infografias/<filename>')
def servir_imagen(filename):
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


@app.route('/generar-imagen', methods=['POST'])
def endpoint_generar_imagen():

    data = request.get_json()
    cedula = data.get('cedula')

    if not cedula:
        return jsonify({"error": "Cédula no proporcionada"}), 400


    df = pd.read_excel('BD.xlsx', dtype={'Cedula': str})
    df['Cedula'] = df['Cedula'].str.strip()

    # Buscar la fila con la cédula
    fila = df[df['Cedula'] == cedula]

    # if fila.empty:
    #     print(f"No se encontró la cédula {cedula_recuperada} en la base de datos.")
    #     sys.exit(1)  # Detener ejecución si no se encontró
    # else:
    #     print("Fila encontrada:", fila)

    # Rutas de la imagen de entrada y salida
    input_image_path = r'Infografias\Infografia.png'

    output_image_path = r'Infografias\Infografia_Personalizada.png'

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


    roboto_black=r'Tipografias\Roboto-Black.ttf'
    roboto_bold=r'Tipografias\Roboto-Bold.ttf'
    roboto_regular=r'Tipografias\Roboto-Regular.ttf'

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
    return jsonify({"imagen_url": f"http://localhost:5001/Infografias/Infografia_Personalizada.png"}), 200

if __name__ == '__main__':
    app.run(port=5001)