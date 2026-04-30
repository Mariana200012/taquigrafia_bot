import sqlite3
import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from fonetizador import texto_a_fonemas
from motor_ia import generar_trazo

# --- CONFIGURACIÓN DE RUTAS ---
DB_PATH = 'data/taquigrafia.db'
ASSETS_PATH = 'assets/gramalogos' 
SIGNOS_PATH = 'assets/signos'

# --- FUNCIONES DE BÚSQUEDA ---
def buscar_en_db(tabla, columna_busqueda, valor):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Usamos LOWER para evitar problemas con mayúsculas
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
    
    # Separar palabras de signos (Ej: "hola, como estas?" -> ["hola", ",", "como", "estas", "?"])
    elementos = re.findall(r'\w+|[^\w\s]', texto_usuario)
    
    fonemas_totales = []
    hay_ia = False

    for item in elementos:
        # 1. ¿ES UN SIGNO DE PUNTUACIÓN?
        # Los signos se suelen enviar por separado porque cortan la liga taquigráfica
        archivo_signo = buscar_en_db('signos', 'signo', item)
        if archivo_signo:
            # Si traíamos fonemas acumulados, los dibujamos antes del signo
            if fonemas_totales:
                ruta_ia = generar_trazo(fonemas_totales)
                with open(ruta_ia, 'rb') as f:
                    await update.message.reply_photo(photo=f, caption="Trazo de la frase hasta el signo.")
                fonemas_totales = [] 

            ruta_s = os.path.join(SIGNOS_PATH, archivo_signo)
            if os.path.exists(ruta_s):
                with open(ruta_s, 'rb') as f:
                    await update.message.reply_photo(photo=f, caption=f"Signo: {item}")
            continue

        # 2. ¿ES UN GRAMÁLOGO?
        # Por ahora, los gramálogos (imágenes fijas) se mandan solos.
        archivo_gram = buscar_en_db('gramalogos', 'palabra', item)
        if archivo_gram:
            # Si hay fonemas previos, dibujarlos
            if fonemas_totales:
                ruta_ia = generar_trazo(fonemas_totales)
                with open(ruta_ia, 'rb') as f:
                    await update.message.reply_photo(photo=f)
                fonemas_totales = []

            ruta_g = os.path.join(ASSETS_PATH, archivo_gram)
            if os.path.exists(ruta_g):
                with open(ruta_g, 'rb') as f:
                    await update.message.reply_photo(photo=f, caption=f"Gramálogo: {item}")
            continue

        # 3. ACUMULAR PARA IA (Escritura corrida)
        fonemas_palabra = texto_a_fonemas(item)
        if fonemas_palabra:
            fonemas_totales.extend(fonemas_palabra)
            hay_ia = True

    # AL FINAL: Generar el gran trazo ligado de toda la frase
    if fonemas_totales:
        await update.message.reply_text("Generando trazo corrido de la frase...")
        ruta_generada = generar_trazo(fonemas_totales)
        if os.path.exists(ruta_generada):
            with open(ruta_generada, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo, 
                    caption=f"Frase corrida: {texto_usuario}\nSonidos: {'-'.join(fonemas_totales)}"
                )
    elif not hay_ia and elementos:
        await update.message.reply_text("No encontré sonidos consonánticos para dibujar esa frase.")

if __name__ == '__main__':
    # Token de tu bot de Telegram
    application = ApplicationBuilder().token('8713996688:AAH0_9hFJrxchmhBYlTuWQ0fIbo9DaBMe_w').build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), procesar_mensaje))
    
    print("Bot activo: Modo frase corrida habilitado.")
    application.run_polling()