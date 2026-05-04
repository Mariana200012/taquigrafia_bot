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
ASSETS_PATH = os.getenv('ASSETS_PATH', 'assets/gramalogos') 
SIGNOS_PATH = os.getenv('SIGNOS_PATH', 'assets/signos')

# --- FUNCIONES DE BÚSQUEDA ---
def buscar_en_db(tabla, columna_busqueda, valor):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"SELECT archivo_imagen FROM {tabla} WHERE LOWER({columna_busqueda}) = ?"
    cursor.execute(query, (valor.lower(),))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

# --- COMANDO DE INICIO ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola Mariana! Soy tu bot de taquigrafía. Escribe una frase y generaré el trazo corrido (ligado) de todas las palabras.")

# --- LÓGICA DE FRASE CORRIDA ---
async def procesar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text.strip()
    
    # Extraemos las palabras o signos usando una expresión regular
    elementos = re.findall(r'\w+|[^\w\s]', texto_usuario)
    fonemas_totales = []
    hay_ia = False

    for item in elementos:
        # 1. ¿Es un signo de puntuación?
        archivo_signo = buscar_en_db('signos', 'signo', item)
        if archivo_signo:
            fonemas_palabra = texto_a_fonemas(item)
            if fonemas_palabra:
                fonemas_totales.extend(fonemas_palabra)
                hay_ia = True
            continue

        # 2. ¿Es un gramálogo?
        archivo_gram = buscar_en_db('gramalogos', 'palabra', item)
        if archivo_gram:
            fonemas_palabra = texto_a_fonemas(item)
            if fonemas_palabra:
                fonemas_totales.extend(fonemas_palabra)
                hay_ia = True
            continue

        # 3. Procesamiento estándar de consonantes
        fonemas_palabra = texto_a_fonemas(item)
        if fonemas_palabra:
            fonemas_totales.extend(fonemas_palabra)
            hay_ia = True

    if fonemas_totales:
        await update.message.reply_text("Generando trazo corrido de la frase...")
        ruta_generada = generar_trazo(lista_fonemas=fonemas_totales)
        
        if os.path.exists(ruta_generada):
            with open(ruta_generada, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo, 
                    caption=f"Escritura corrida: {texto_usuario}\nSonidos: {'-'.join(fonemas_totales)}"
                )
    else:
        await update.message.reply_text("No encontré sonidos consonánticos para dibujar esa frase.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), procesar_mensaje))
    
    print("Bot activo y configurado de forma segura.")
    application.run_polling()