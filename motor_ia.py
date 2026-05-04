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
    
    # Dibujar Renglón
    y_renglon = 250
    draw.line([(50, y_renglon), (750, y_renglon)], fill=(200, 220, 255), width=2)
    
    # --- POSICIONAMIENTO INICIAL GLOBAL ---
    x_actual = 150 
    largo = 60 

    if lista_fonemas:
        primer_dato = obtener_datos(lista_fonemas[0])
        if primer_dato:
            sentido_inicial = str(primer_dato[5]).lower()
            if "descendente" in sentido_inicial:
                y_actual = y_renglon - largo 
            elif "horizontal" in sentido_inicial:
                y_actual = y_renglon - 5
            elif "ascendente" in sentido_inicial:
                y_actual = y_renglon
            else:
                y_actual = y_renglon
        else:
            y_actual = y_renglon
    else:
        y_actual = y_renglon

    for fonema in lista_fonemas:
        datos = obtener_datos(fonema)
        if datos is None: 
            continue
        
        tipo = datos[1]
        grosor = datos[2]
        orientacion = str(datos[4]).lower()
        sentido = str(datos[5]).lower()
        
        try:
            angulo_orig = float(str(datos[3]).replace('°', '').strip())
            radianes = math.radians(angulo_orig)
        except: 
            continue

        # --- POSICIONAMIENTO DINÁMICO POR LETRA ---
        if "ascendente" in sentido:
            y_actual = y_renglon
        elif "descendente" in sentido:
            if fonema != lista_fonemas[0]:
                y_actual = y_renglon - largo
        elif "horizontal" in sentido:
            y_actual = y_renglon - 5

        x_final = x_actual + largo * math.cos(radianes)
        y_final = y_actual + largo * math.sin(radianes)
        
        ancho = 5 if grosor == 'grueso' else 2

        if tipo == 'recto':
            draw.line([(x_actual, y_actual), (x_final, y_final)], fill="black", width=ancho)
        else:
            # --- LÓGICA DE CURVATURA ESTILIZADA ---
            dist_curva = 15  # Radio del arco para trazos horizontales
            
            # --- DIRECCIÓN ESTRICTA DE LA CURVA ---
            if fonema == 'el' or fonema == 'er':
                fuerza_angulo = radianes - math.pi / 2
            elif "abajo" in orientacion:
                # "me" abre hacia abajo
                fuerza_angulo = radianes + math.pi / 2
            elif "arriba" in orientacion or "ne" in fonema or "ñe" in fonema:
                # "ne" y "ñe" abren hacia arriba
                fuerza_angulo = radianes - math.pi / 2
            elif "derecha" in orientacion:
                fuerza_angulo = radianes + math.pi / 2
            elif "izquierda" in orientacion:
                fuerza_angulo = radianes - math.pi / 2
            else:
                fuerza_angulo = radianes - math.pi / 2

            # Punto de control para la curva de Bézier
            cx = (x_actual + x_final)/2 + dist_curva * math.cos(fuerza_angulo)
            cy = (y_actual + y_final)/2 + dist_curva * math.sin(fuerza_angulo)
            
            puntos = []
            for t in [i/10 for i in range(11)]:
                px = (1-t)**2 * x_actual + 2*(1-t)*t * cx + t**2 * x_final
                py = (1-t)**2 * y_actual + 2*(1-t)*t * cy + t**2 * y_final
                puntos.append((px, py))
            draw.line(puntos, fill="black", width=ancho)

        # Actualizar posición para el siguiente fonema
        x_actual, y_actual = x_final, y_final
        
    ruta = "assets/temp_generado.png"
    img.save(ruta)
    return ruta