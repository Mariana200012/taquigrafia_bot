import sqlite3
import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from fonetizador import texto_a_fonemas
from motor_ia import generar_trazo

# --- CARGAR VARIABLES DE ENTORNO ---
load_dotenv()

# --- CONFIGURACIÓN DE RUTAS Y TOKEN ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DB_PATH = os.getenv('DB_PATH', 'data/taquigrafia.db')
BASE_ASSETS = os.getenv('ASSETS_PATH', 'assets')

# --- FUNCIONES DE BÚSQUEDA ---
def buscar_en_db(tabla, columna_busqueda, valor, columna_retorno='archivo_imagen'):
    """Busca en la DB y devuelve el nombre del archivo de imagen."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = f"SELECT {columna_retorno} FROM {tabla} WHERE LOWER({columna_busqueda}) = ?"
        cursor.execute(query, (valor.lower(),))
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"Error al buscar en DB ({tabla}): {e}")
        return None

# --- COMANDO DE INICIO ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola Mariana! Soy tu bot de taquigrafía.\n\n"
        "Escribe una frase y generaré el trazo híbrido ligado, o enviaré "
        "la imagen directa si es un gramálogo."
    )

# --- LÓGICA DE CONTROL ---
async def procesar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text.strip()
    item_lower = texto_usuario.lower()
    
    # --- PASO 1: ¿TODA LA FRASE ES UN GRAMÁLOGO O SIGNO? ---
    archivo_signo = buscar_en_db('signos', 'signo', item_lower)
    if archivo_signo:
        ruta_signo = os.path.join(BASE_ASSETS, 'signos', archivo_signo)
        if os.path.exists(ruta_signo):
            with open(ruta_signo, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=f"Signo: {texto_usuario}")
            return

    archivo_gram = buscar_en_db('gramalogos', 'palabra', item_lower)
    if archivo_gram:
        ruta_gram = os.path.join(BASE_ASSETS, 'gramalogos', archivo_gram)
        if os.path.exists(ruta_gram):
            with open(ruta_gram, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=f"Gramálogo: {texto_usuario}")
            return

    # --- PASO 2: PROCESAMIENTO DE ELEMENTOS ---
    elementos = re.findall(r'\w+|[^\w\s]', texto_usuario)
    elementos_procesados = []

    for item in elementos:
        item_l = item.lower()
        
        # ¿Es gramálogo o signo individual?
        es_gram = buscar_en_db('gramalogos', 'palabra', item_l)
        es_sig = buscar_en_db('signos', 'signo', item_l)
        
        if es_gram or es_sig:
            elementos_procesados.append(item_l)
            continue

        # Si no, usamos el fonetizador (que ahora devuelve diccionarios con posición)
        fonemas_palabra = texto_a_fonemas(item_l)
        if fonemas_palabra:
            elementos_procesados.extend(fonemas_palabra)

    # --- PASO 3: GENERACIÓN DE IMAGEN HÍBRIDA ---
    if elementos_procesados:
        await update.message.reply_text("Analizando secuencia... Generando trazo híbrido.")
        try:
            # Enviamos la lista (con diccionarios) al motor
            ruta_generada = generar_trazo(lista_fonemas=elementos_procesados)
            
            if os.path.exists(ruta_generada):
                # LIMPIEZA DE SECUENCIA PARA EL CAPTION
                # Extraemos solo el texto del sonido para que .join() no falle
                secuencia_texto = "-".join([
                    e['sonido'] if isinstance(e, dict) else e 
                    for e in elementos_procesados
                ])

                with open(ruta_generada, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo, 
                        caption=f"Escritura ligada: {texto_usuario}\nSecuencia: {secuencia_texto}"
                    )
        except Exception as e:
            await update.message.reply_text(f"Error en el motor híbrido: {e}")
    else:
        await update.message.reply_text("No identifiqué elementos para dibujar.")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("ERROR: No se encontró el TELEGRAM_BOT_TOKEN en .env")
    else:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), procesar_mensaje))
        
        print("Bot iniciado con soporte para posiciones y concavidad.")
        application.run_polling()