import math
from PIL import Image, ImageDraw
import sqlite3

def obtener_datos_consonante(fonema):
    conn = sqlite3.connect('data/taquigrafia.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tipo_trazo, grosor, angulo FROM consonantes WHERE fonema = ?", (fonema,))
    res = cursor.fetchone()
    conn.close()
    return res

def generar_trazo(lista_fonemas):
    # Crear un lienzo blanco (RGBA para transparencia si quieres)
    img = Image.new('RGB', (600, 400), 'white')
    draw = ImageDraw.Draw(img)
    
    # Punto inicial (centro del lienzo)
    x_actual, y_actual = 100, 200
    largo_trazo = 50 # Longitud de cada letra
    
    for fonema in lista_fonemas:
        datos = obtener_datos_consonante(fonema)
        if not datos: continue
        
        tipo, grosor, angulo_grados = datos
        
        # --- LA MATEMÁTICA DE LA IA ---
        # Convertimos grados a radianes porque Python usa radianes
        # Nota: En taquigrafía, los ángulos suelen medirse distinto al círculo unitario estándar,
        # ajustamos para que 90° sea hacia abajo y 180° a la izquierda.
        radianes = math.radians(angulo_grados)
        
        x_final = x_actual + largo_trazo * math.cos(radianes)
        y_final = y_actual + largo_trazo * math.sin(radianes)
        
        # Configurar grosor
        ancho = 5 if grosor == 'grueso' else 2
        
        # Dibujar (Si es recto)
        if tipo == 'recto':
            draw.line([(x_actual, y_actual), (x_final, y_final)], fill="black", width=ancho)
        else:
            # Aquí podrías programar arcos para los "curvos"
            # Por ahora, para que funcione, haremos una línea punteada o curva simple
            draw.line([(x_actual, y_actual), (x_final, y_final)], fill="blue", width=ancho)
        
        # El final de esta letra es el inicio de la siguiente
        x_actual, y_actual = x_final, y_final
        
    # Guardar imagen temporal
    ruta_salida = "assets/temp_generado.png"
    img.save(ruta_salida)
    return ruta_salida