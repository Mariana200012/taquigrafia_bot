import math
from PIL import Image, ImageDraw
import sqlite3
import os

def obtener_datos_consonante(fonema):
    conn = sqlite3.connect('data/taquigrafia.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tipo_trazo, grosor, angulo FROM consonantes WHERE fonema = ?", (fonema,))
    res = cursor.fetchone()
    conn.close()
    return res

def generar_trazo(lista_fonemas):
    # Asegurarnos de que la carpeta assets exista para guardar el temporal
    if not os.path.exists('assets'):
        os.makedirs('assets')

    # Crear un lienzo blanco
    img = Image.new('RGB', (600, 400), 'white')
    draw = ImageDraw.Draw(img)
    
    # Punto inicial
    x_actual, y_actual = 150, 200
    largo_trazo = 60 
    
    for fonema in lista_fonemas:
        datos = obtener_datos_consonante(fonema)
        if not datos: 
            print(f"Fonema {fonema} no encontrado en la DB.")
            continue
        
        tipo, grosor, angulo_sucio = datos
        
        # --- LIMPIEZA DE DATOS CRÍTICA ---
        try:
            # Quitamos el símbolo de grado y convertimos a número decimal
            angulo_numerico = float(str(angulo_sucio).replace('°', '').strip())
            radianes = math.radians(angulo_numerico)
        except (ValueError, TypeError):
            print(f"Error: No se pudo convertir el ángulo '{angulo_sucio}' a número.")
            continue

        # Calcular coordenadas finales
        # Usamos seno y coseno para la trayectoria geométrica
        x_final = x_actual + largo_trazo * math.cos(radianes)
        y_final = y_actual + largo_trazo * math.sin(radianes)
        
        # Configurar grosor según la tabla
        ancho = 5 if grosor == 'grueso' else 2
        
        # Dibujar según el tipo
        color = "black"
        if tipo == 'recto':
            draw.line([(x_actual, y_actual), (x_final, y_final)], fill=color, width=ancho)
        else:
            # Por ahora dibujamos recto, pero en azul para distinguir los curvos
            draw.line([(x_actual, y_actual), (x_final, y_final)], fill="blue", width=ancho)
        
        # Actualizar posición para el siguiente fonema (encadenamiento)
        x_actual, y_actual = x_final, y_final
        
    # Guardar imagen temporal
    ruta_salida = "assets/temp_generado.png"
    img.save(ruta_salida)
    return ruta_salida