from flask import Flask, render_template, request, jsonify
import json
from pathlib import Path
from maquina_turing import MaquinaTuring

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent

# Variable global para mantener viva la máquina mientras el usuario interactúa
maquina_actual = None 

@app.route('/')
def index():
    # Cuando entres a localhost:5000, Flask enviará el archivo HTML
    return render_template('index.html')

@app.route('/cargar', methods=['POST'])
def cargar():
    """Recibe el tipo de máquina y la palabra inicial desde la web."""
    global maquina_actual
    datos = request.get_json(silent=True) or {}
    maquina_tipo = datos.get('tipo')
    entrada = datos.get('entrada', '')

    if maquina_tipo not in ('suma', '0n1n'):
        return jsonify({"error": "Tipo de máquina no válido"}), 400

    if not isinstance(entrada, str):
        return jsonify({"error": "La entrada debe ser texto"}), 400

    # Elegimos el "cartucho" correcto según el botón que toque el usuario
    archivo_json = BASE_DIR / ('suma_unaria.json' if maquina_tipo == 'suma' else 'ceros_unos.json')
    
    try:
        with archivo_json.open('r', encoding='utf-8') as f:
            config = json.load(f)
            
        maquina_actual = MaquinaTuring(config)
        maquina_actual.cargar_entrada(entrada)
        
        # Devolvemos el estado inicial de la cinta para que la web la dibuje
        return jsonify(maquina_actual.obtener_estado_actual())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/step', methods=['POST'])
def step():
    """Da un solo paso en la máquina de Turing y devuelve el resultado."""
    global maquina_actual
    if not maquina_actual:
        return jsonify({"error": "Máquina no cargada"}), 400
    
    maquina_actual.step()
    return jsonify(maquina_actual.obtener_estado_actual())

if __name__ == '__main__':
    # Arranca el servidor local en modo desarrollo
    app.run(debug=True)