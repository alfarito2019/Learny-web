from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import subprocess
import os

app = Flask(__name__)
CORS(app)

# Cargar BD una vez
bd_path = os.path.abspath("C:/Users/juanf/Desktop/Learny/BD.xlsx")  # Ajusta si está en otra ruta
if not os.path.exists(bd_path):
    raise FileNotFoundError("No se encontró BD.xlsx")

df = pd.read_excel(bd_path)
df["Cedula"] = df["Cedula"].astype(str).str.replace(".0", "", regex=False)
df["Clave"] = df["Clave"].astype(str).str.replace(".0", "", regex=False)

# Ruta de prueba simple
@app.get("/")
def inicio():
    return "✅ Servidor Flask funcionando"

# Ruta de login
@app.post("/login")
def login():
    data = request.get_json()
    cedula = data.get("cedula")
    clave = data.get("clave")

    cliente = df[(df["Cedula"] == cedula) & (df["Clave"] == clave)]
    if not cliente.empty:
        nombre = cliente.iloc[0]["Nombre"]
        return jsonify({"status": "ok", "nombre": nombre})
    else:
        return jsonify({"status": "error", "detail": "Credenciales incorrectas"}), 401

# Ruta para generar infografía
@app.post("/infografia/<cedula>")
def generar_infografia(cedula):
    try:
        resultado = subprocess.run(["python", "imagen.py", cedula], capture_output=True, text=True)
        return jsonify({"status": "ok", "output": resultado.stdout})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
