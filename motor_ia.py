import math
from PIL import Image, ImageDraw
import sqlite3
import os

def obtener_datos_completos(elemento):
    conn = sqlite3.connect('data/taquigrafia.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM signos WHERE signo = ?", (elemento,))
        res = cursor.fetchone()
        if res and 'archivo_imagen' in res.keys() and res['archivo_imagen']:
            return {'tipo': 'imagen', 'ruta': f"assets/signos/{res['archivo_imagen']}"}
        cursor.execute("SELECT * FROM gramalogos WHERE palabra = ?", (elemento,))
        res = cursor.fetchone()
        if res and 'archivo_imagen' in res.keys() and res['archivo_imagen']:
            return {'tipo': 'imagen', 'ruta': f"assets/gramalogos/{res['archivo_imagen']}"}
        cursor.execute("SELECT * FROM consonantes WHERE fonema = ?", (elemento,))
        res = cursor.fetchone()
        if res:
            return {
                'tipo': 'trazo',
                'fonema': res['fonema'],
                'forma': res['tipo_trazo'],
                'grosor': res['grosor'],
                'angulo': res['angulo'],
                'orientacion': res['orientacion'] if res['orientacion'] else 'N/A',
                'sentido': res['sentido'].lower() if res['sentido'] else 'ascendente'
            }
    except Exception as e:
        print(f"Error en consulta DB: {e}")
    finally:
        conn.close()
    return None

def generar_trazo(lista_fonemas):
    lista_limpia = []
    posicion_global = 2 
    if len(lista_fonemas) > 0 and isinstance(lista_fonemas[0], dict):
        posicion_global = lista_fonemas[0].get('posicion', 2)
        lista_limpia = [f['sonido'] for f in lista_fonemas]
    else:
        lista_limpia = lista_fonemas

    img = Image.new('RGB', (1000, 500), 'white')
    draw = ImageDraw.Draw(img)
    y_renglon_base = 300
    draw.line([(50, y_renglon_base), (950, y_renglon_base)], fill=(200, 220, 255), width=2)
    
    x_actual = 100
    largo_trazo = 60 

    primer_datos = obtener_datos_completos(lista_limpia[0])
    
    # --- LÓGICA DE ALTURA: PANZA ABAJO SE LEVANTA ---
    if posicion_global == 2:
        y_renglon_trabajo = y_renglon_base
        if primer_datos and primer_datos['sentido'] == 'horizontal':
            # Si en la BD dice "abajo" (como ne/ñe), subimos el trazo para que la panza apoye
            if "abajo" in str(primer_datos['orientacion']).lower():
                dist_v = 30 if primer_datos['fonema'].lower() in ['me', 'ne', 'ñe'] else 18
                y_renglon_trabajo = y_renglon_base - dist_v
            else:
                # Si es "arriba" (como me) o recto (que), va pegado a la línea
                y_renglon_trabajo = y_renglon_base - 2
    elif posicion_global == 1:
        y_renglon_trabajo = y_renglon_base - 80 
    else:
        y_renglon_trabajo = y_renglon_base + 30

    y_actual = y_renglon_trabajo
    
    if primer_datos and "descendente" in primer_datos['sentido']:
        ang_ini = float(str(primer_datos['angulo']).replace('°', '').strip() or 0)
        y_actual = y_renglon_trabajo - abs(largo_trazo * math.sin(math.radians(ang_ini)))

    for elemento in lista_limpia:
        datos = obtener_datos_completos(elemento)
        if not datos: continue
        try:
            ang_val = float(str(datos['angulo']).replace('°', '').strip() or 0)
            radianes = math.radians(ang_val)
            x_final = x_actual + (largo_trazo * math.cos(radianes))
            y_final = y_actual - (largo_trazo * math.sin(radianes))
            ancho = 5 if datos['grosor'].lower() == 'grueso' else 2

            if datos['forma'] == 'recto':
                draw.line([(x_actual, y_actual), (x_final, y_final)], fill="black", width=ancho)
            else:
                fonema_nom = datos['fonema'].lower()
                dist_curva = 30 if fonema_nom in ['me', 'ne', 'ñe', 'es'] else 18
                
                # --- CORRECCIÓN DE ORIENTACIÓN SOLICITADA ---
                # "arriba" resta en Y (sube la panza)
                # "abajo" suma en Y (baja la panza)
                if "arriba" in str(datos['orientacion']).lower():
                    f_ang = radianes - (math.pi / 2)
                else:
                    f_ang = radianes + (math.pi / 2)

                cx = (x_actual + x_final)/2 + dist_curva * math.cos(f_ang)
                cy = (y_actual + y_final)/2 + dist_curva * math.sin(f_ang)
                
                puntos = []
                for t in [i/15 for i in range(16)]:
                    px = (1-t)**2 * x_actual + 2*(1-t)*t * cx + t**2 * x_final
                    py = (1-t)**2 * y_actual + 2*(1-t)*t * cy + t**2 * y_final
                    puntos.append((px, py))
                draw.line(puntos, fill="black", width=ancho)

            x_actual, y_actual = x_final, y_final
        except Exception as e:
            print(f"Error: {e}")

    ruta = "assets/temp_generado.png"
    img.save(ruta)
    return ruta