import json
from flask import Flask, render_template, request, jsonify, send_from_directory
import random
import unicodedata
import os
import re
from urllib.parse import unquote

# --- 1. Inicialización de la Aplicación Flask (¡SOLO UNA VEZ!) ---
app = Flask(__name__)

# --- 2. Ruta para servir el Service Worker desde la raíz del proyecto ---
@app.route('/service-worker.js')
def serve_sw():
    # Sirve el service-worker.js desde la raíz del proyecto
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(root_dir, 'service-worker.js')

# --- 3. Definición de la ruta base para los archivos de datos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- 4. Carga de los archivos JSON (¡SOLO UNA VEZ Y ANTES DE LAS RUTAS!) ---
try:
    with open(os.path.join(BASE_DIR, 'biblia.json'), 'r', encoding='utf-8') as f:
        biblia = json.load(f)
    print("biblia.json cargado exitosamente.")
except FileNotFoundError:
    print(f"Error: 'biblia.json' no encontrado en '{BASE_DIR}'.")
    biblia = {}
except json.JSONDecodeError:
    print("Error: 'biblia.json' contiene un JSON inválido.")
    biblia = {}

try:
    with open(os.path.join(BASE_DIR, 'resumen_libros.json'), 'r', encoding='utf-8') as f:
        resumenes_libros = json.load(f)
    print("resumen_libros.json cargado exitosamente.")
except FileNotFoundError:
    print(f"Error: 'resumen_libros.json' no encontrado en '{BASE_DIR}'.")
    resumenes_libros = {}
except json.JSONDecodeError:
    print("Error: 'resumen_libros.json' contiene un JSON inválido.")
    resumenes_libros = {}

# --- 5. Función para normalizar texto (utilizada en la búsqueda) ---
def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return text

# --- 6. Definición de todas las Rutas de la Aplicación ---
@app.route('/')
def index():
    versiculo_aleatorio_texto = "¡Bienvenido a tu Biblia App! Navega para empezar."
    versiculo_aleatorio_referencia = ""
    biblia_data_contenido = biblia.get('biblia_data', {})
    if biblia_data_contenido:
        libros_disponibles = [nombre for nombre in biblia_data_contenido.keys() if nombre != 'info']
        if libros_disponibles:
            libro_elegido_nombre = random.choice(libros_disponibles)
            libro_elegido_data = biblia_data_contenido.get(libro_elegido_nombre, {})
            capitulos_disponibles = [cap for cap in libro_elegido_data.keys() if cap != 'info']
            if capitulos_disponibles:
                capitulo_elegido_num = random.choice(capitulos_disponibles)
                versiculos_capitulo = libro_elegido_data.get(capitulo_elegido_num, {})
                versiculos_nums = [v_num for v_num in versiculos_capitulo.keys()]
                if versiculos_nums:
                    versiculo_elegido_num = random.choice(versiculos_nums)
                    versiculo_aleatorio_texto = versiculos_capitulo.get(versiculo_elegido_num)
                    versiculo_aleatorio_referencia = f"{libro_elegido_nombre} {capitulo_elegido_num}:{versiculo_elegido_num}"
    return render_template('index.html',
                           portada_versiculo=versiculo_aleatorio_texto,
                           portada_referencia=versiculo_aleatorio_referencia,
                           libros=biblia_data_contenido.keys(),
                           resumenes_libros=resumenes_libros)

@app.route('/libros')
def lista_libros():
    nombres_libros = biblia.get('biblia_data', {}).keys()
    libros_ordenados = sorted(nombres_libros)
    return render_template('libros.html', libros=libros_ordenados, resumenes_libros=resumenes_libros)

@app.route('/libro/<nombre_libro>')
def ver_libro(nombre_libro):
    nombre_libro_decodificado = unquote(nombre_libro)
    libro_data = biblia.get('biblia_data', {}).get(nombre_libro_decodificado, None)
    if libro_data:
        capitulos = [cap for cap in libro_data.keys() if cap != 'info']
        capitulos_ordenados = sorted(capitulos, key=int)
        resumen = resumenes_libros.get(nombre_libro_decodificado, "Resumen no disponible.")
        return render_template('ver_libro.html',
                               libro_nombre=nombre_libro_decodificado,
                               capitulos=capitulos_ordenados,
                               resumen=resumen)
    else:
        return render_template('error.html', mensaje=f"Lo siento, el libro '{nombre_libro_decodificado}' no fue encontrado.", titulo_error="Libro no Encontrado"), 404

@app.route('/libro/<nombre_libro>/capitulo/<int:num_capitulo>')
def ver_capitulo(nombre_libro, num_capitulo):
    nombre_libro_decodificado = unquote(nombre_libro)
    libro_data = biblia.get('biblia_data', {}).get(nombre_libro_decodificado, None)
    if libro_data:
        capitulos_disponibles = [int(c) for c in libro_data.keys() if c != 'info']
        capitulos_ordenados = sorted(capitulos_disponibles)
        capitulo_data = libro_data.get(str(num_capitulo), None)
        if capitulo_data:
            versiculos_ordenados = sorted(capitulo_data.items(), key=lambda item: int(item[0]))
            indice_actual = capitulos_ordenados.index(num_capitulo)
            capitulo_anterior = capitulos_ordenados[indice_actual - 1] if indice_actual > 0 else None
            capitulo_siguiente = capitulos_ordenados[indice_actual + 1] if indice_actual < len(capitulos_ordenados) - 1 else None
            return render_template('ver_capitulo.html',
                                   libro_nombre=nombre_libro_decodificado,
                                   num_capitulo=num_capitulo,
                                   versiculos=versiculos_ordenados,
                                   capitulo_anterior=capitulo_anterior,
                                   capitulo_siguiente=capitulo_siguiente,
                                   todos_los_capitulos=capitulos_ordenados)
        else:
            return render_template('error.html', mensaje=f"Capítulo {num_capitulo} no encontrado para el libro {nombre_libro_decodificado}.", titulo_error="Capítulo no Encontrado"), 404
    else:
        return render_template('error.html', mensaje=f"Lo siento, el libro '{nombre_libro_decodificado}' no fue encontrado.", titulo_error="Libro no Encontrado"), 404

@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q', '').strip()
    resultados = []
    if query:
        query_normalized = normalize_text(query)
        for libro_nombre, libro_contenido in biblia.get('biblia_data', {}).items():
            if libro_nombre == 'info':
                continue
            for num_capitulo, capitulo_versiculos in libro_contenido.items():
                if num_capitulo == 'info':
                    continue
                for num_versiculo, texto_versiculo in capitulo_versiculos.items():
                    texto_normalized = normalize_text(texto_versiculo)
                    if query_normalized in texto_normalized:
                        resultados.append({
                            'libro': libro_nombre,
                            'capitulo': num_capitulo,
                            'versiculo_num': num_versiculo,
                            'texto': texto_versiculo
                        })
    resultados_ordenados = sorted(resultados, key=lambda x: (x['libro'], int(x['capitulo']), int(x['versiculo_num'])))
    return render_template('resultados_busqueda.html',
                           query=query,
                           resultados=resultados_ordenados)

@app.route('/favoritos')
def mostrar_favoritos():
    return render_template('favoritos.html')

# --- 7. Ejecutar la Aplicación ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')