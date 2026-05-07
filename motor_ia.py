import math
from PIL import Image, ImageDraw
import sqlite3
import os

def obtener_datos_completos(elemento):
    """Busca en todas las tablas y devuelve un diccionario con lo que encuentre."""
    conn = sqlite3.connect('data/taquigrafia.db')
    conn.row_factory = sqlite3.Row  # Permite acceder por nombre de columna
    cursor = conn.cursor()
    
    try:
        # 1. Buscar en SIGNOS
        cursor.execute("SELECT * FROM signos WHERE signo = ?", (elemento,))
        res = cursor.fetchone()
        if res and 'archivo_imagen' in res.keys() and res['archivo_imagen']:
            return {'tipo': 'imagen', 'ruta': f"assets/signos/{res['archivo_imagen']}"}

        # 2. Buscar en GRAMALOGOS
        cursor.execute("SELECT * FROM gramalogos WHERE palabra = ?", (elemento,))
        res = cursor.fetchone()
        if res and 'archivo_imagen' in res.keys() and res['archivo_imagen']:
            return {'tipo': 'imagen', 'ruta': f"assets/gramalogos/{res['archivo_imagen']}"}

        # 3. Buscar en CONSONANTES (Basado en tu CSV: fonema, tipo_trazo, grosor, angulo...)
        cursor.execute("SELECT * FROM consonantes WHERE fonema = ?", (elemento,))
        res = cursor.fetchone()
        
        if res:
            return {
                'tipo': 'trazo',
                'forma': res['tipo_trazo'],  # Nombre exacto en tu CSV
                'grosor': res['grosor'],     # delgado / grueso
                'angulo': res['angulo'],
                'orientacion': res['orientacion'] if 'orientacion' in res.keys() else 'N/A',
                'sentido': res['sentido'] if 'sentido' in res.keys() else 'ascendente'
            }
    except Exception as e:
        print(f"Error en consulta DB: {e}")
    finally:
        conn.close()
    return None

def generar_trazo(lista_fonemas):
    # Lienzo amplio para escritura corrida
    img = Image.new('RGB', (1000, 500), 'white')
    draw = ImageDraw.Draw(img)
    
    # Dibujar Renglón de referencia
    y_renglon = 300
    draw.line([(50, y_renglon), (950, y_renglon)], fill=(200, 220, 255), width=2)
    
    x_actual, y_actual = 100, y_renglon
    largo_trazo = 60 

    for elemento in lista_fonemas:
        datos = obtener_datos_completos(elemento)
        if not datos:
            print(f"Saltando {elemento}: No se encontró en la DB")
            continue

        # --- CASO A: ES IMAGEN (Gramálogo o Signo) ---
        if datos['tipo'] == 'imagen':
            if os.path.exists(datos['ruta']):
                with Image.open(datos['ruta']) as img_p:
                    img_p = img_p.convert("RGBA")
                    # Ajustar tamaño para que sea proporcional al trazo
                    img_p.thumbnail((50, 50)) 
                    # Pegar centrando verticalmente sobre el punto actual
                    img.paste(img_p, (int(x_actual), int(y_actual - 25)), img_p)
                    x_actual += img_p.width + 5 # Espaciado
            continue

        # --- CASO B: ES TRAZO TÉCNICO (Consonantes) ---
        try:
            # Limpieza de ángulo (maneja strings o números)
            angulo_raw = str(datos['angulo']).replace('°', '').strip()
            if angulo_raw == 'N/A': angulo_raw = '0'
            radianes = math.radians(float(angulo_raw))
            
            # Cálculo de punto final
            x_final = x_actual + largo_trazo * math.cos(radianes)
            y_final = y_actual + largo_trazo * math.sin(radianes)
            
            # Grosor según tu CSV (delgado o grueso)
            ancho = 5 if datos['grosor'].lower() == 'grueso' else 2

            if datos['forma'] == 'recto':
                draw.line([(x_actual, y_actual), (x_final, y_final)], fill="black", width=ancho)
            else:
                # Lógica de Curva (Pitman/Sánchez-Osornio)
                dist_curva = 18 
                orientacion = datos['orientacion'].lower()
                
                # Determinar hacia dónde "pandea" la curva
                if "izquierda" in orientacion:
                    fuerza_angulo = radianes - math.pi / 2
                elif "derecha" in orientacion:
                    fuerza_angulo = radianes + math.pi / 2
                else:
                    fuerza_angulo = radianes - math.pi / 2 # Default arriba/izquierda

                # Punto de control Bézier
                cx = (x_actual + x_final)/2 + dist_curva * math.cos(fuerza_angulo)
                cy = (y_actual + y_final)/2 + dist_curva * math.sin(fuerza_angulo)
                
                puntos_curva = []
                for t in [i/15 for i in range(16)]:
                    px = (1-t)**2 * x_actual + 2*(1-t)*t * cx + t**2 * x_final
                    py = (1-t)**2 * y_actual + 2*(1-t)*t * cy + t**2 * y_final
                    puntos_curva.append((px, py))
                
                draw.line(puntos_curva, fill="black", width=ancho)

            # Actualizar coordenadas para ligar el siguiente trazo
            x_actual, y_actual = x_final, y_final

        except Exception as e:
            print(f"Error dibujando el elemento '{elemento}': {e}")

    # Guardar y retornar ruta
    if not os.path.exists('assets'): os.makedirs('assets')
    ruta = "assets/temp_generado.png"
    img.save(ruta)
    return ruta