import math
from PIL import Image, ImageDraw
import sqlite3
import os

def obtener_datos(fonema, tabla='consonantes'):
    """Obtiene la configuración geométrica desde la base de datos."""
    conn = sqlite3.connect('data/taquigrafia.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {tabla} WHERE fonema = ?", (fonema,))
    res = cursor.fetchone()
    conn.close()
    return res

def generar_trazo(lista_fonemas):
    """Genera una imagen con el trazo taquigráfico sobre un renglón."""
    if not os.path.exists('assets'): 
        os.makedirs('assets')

    # Configuración del lienzo
    img = Image.new('RGB', (800, 400), 'white')
    draw = ImageDraw.Draw(img)
    
    # Dibujar Renglón (Referencia visual de contexto)
    y_renglon = 250
    draw.line([(50, y_renglon), (750, y_renglon)], fill=(200, 220, 255), width=2)
    
    # --- IA DE POSICIONAMIENTO INICIAL ---
    x_actual = 150 
    largo = 60 

    # Ajuste de altura inicial basado en el primer fonema
    if lista_fonemas:
        primer_dato = obtener_datos(lista_fonemas[0])
        if primer_dato:
            sentido = str(primer_dato[5]).lower()
            
            if "descendente" in sentido:
                # Empieza arriba para terminar tocando el renglón
                y_actual = y_renglon - largo 
            elif "horizontal" in sentido:
                # Flota ligeramente sobre el renglón para mayor claridad
                y_actual = y_renglon - 5
            else:
                # Ascendentes empiezan exactamente sobre el renglón
                y_actual = y_renglon
        else:
            y_actual = y_renglon
    else:
        y_actual = y_renglon

    for fonema in lista_fonemas:
        datos = obtener_datos(fonema)
        
        # Seguridad para evitar errores si el fonema no existe
        if datos is None: 
            continue
        
        tipo = datos[1]
        grosor = datos[2]
        orientacion = str(datos[4]).lower()
        
        try:
            # Limpieza y conversión de ángulos
            angulo_orig = float(str(datos[3]).replace('°', '').strip())
            radianes = math.radians(angulo_orig)
        except: 
            continue

        x_final = x_actual + largo * math.cos(radianes)
        y_final = y_actual + largo * math.sin(radianes)
        
        # Grosor dinámico (IA visual)
        ancho = 5 if grosor == 'grueso' else 2

        if tipo == 'recto':
            draw.line([(x_actual, y_actual), (x_final, y_final)], fill="black", width=ancho)
        else:
            # --- LÓGICA DE CURVATURA DE PRECISIÓN ---
            dist_curva = 35 # Radio del arco
            
            # Determinamos la dirección de la "panza" del trazo
            if "arriba" in orientacion:
                fuerza_angulo = radianes - math.pi/2
            elif "abajo" in orientacion:
                fuerza_angulo = radianes + math.pi/2
            elif "derecha" in orientacion:
                # Para trazos como 'fe' o 've'
                fuerza_angulo = radianes + math.pi/2 
            elif "izquierda" in orientacion:
                # Para trazos como 'er', 'el', 'es'
                fuerza_angulo = radianes - math.pi/2
            else:
                fuerza_angulo = radianes - math.pi/2

            # Punto de control para la curva de Bézier
            cx = (x_actual + x_final)/2 + dist_curva * math.cos(fuerza_angulo)
            cy = (y_actual + y_final)/2 + dist_curva * math.sin(fuerza_angulo)
            
            # Dibujo suavizado por pasos
            puntos = []
            for t in [i/10 for i in range(11)]:
                px = (1-t)**2 * x_actual + 2*(1-t)*t * cx + t**2 * x_final
                py = (1-t)**2 * y_actual + 2*(1-t)*t * cy + t**2 * y_final
                puntos.append((px, py))
            draw.line(puntos, fill="black", width=ancho)

        # Actualizar posición para el siguiente fonema (trazos ligados)
        x_actual, y_actual = x_final, y_final
        
    ruta = "assets/temp_generado.png"
    img.save(ruta)
    return ruta