import sqlite3
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
# Importamos tus nuevos módulos de IA
from fonetizador import texto_a_fonemas
from motor_ia import generar_trazo

# --- CONFIGURACIÓN DE RUTAS ---
DB_PATH = 'data/taquigrafia.db'
ASSETS_PATH = 'assets/gramalogos' 

# --- FUNCIÓN DE BÚSQUEDA EN BASE DE DATOS ---
def buscar_gramalogo(palabra_usuario):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT archivo_imagen FROM gramalogos WHERE palabra = ?"
    cursor.execute(query, (palabra_usuario.lower(),))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

# --- COMANDO DE INICIO ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu bot de taquigrafía. Escribe una palabra y si no es un gramálogo, ¡la dibujaré usando IA!")

# --- LÓGICA PRINCIPAL DEL MENSAJE ---
async def procesar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    palabra = update.message.text.strip().lower()
    
    # 1. Intentar buscar como gramálogo (Imagen fija)
    archivo_imagen = buscar_gramalogo(palabra)
    
    if archivo_imagen:
        ruta_completa = os.path.join(ASSETS_PATH, archivo_imagen)
        if os.path.exists(ruta_completa):
            with open(ruta_completa, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=f"Gramálogo: {palabra}")
        else:
            await update.message.reply_text(f"Error: No encontré la imagen fija para {palabra}.")
            
    else:
        # 2. SI NO ES GRAMÁLOGO, ENTRA LA IA (Dibujo dinámico)
        await update.message.reply_text(f"'{palabra}' no es un gramálogo. Generando trazo con IA...")
        
        # Convertimos a sonidos
        fonemas = texto_a_fonemas(palabra)
        
        if fonemas:
            # Generamos el dibujo basado en geometría
            ruta_generada = generar_trazo(fonemas)
            
            with open(ruta_generada, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=f"Trazo generado para los sonidos: {', '.join(fonemas)}")
        else:
            await update.message.reply_text("No pude identificar los sonidos de esa palabra para dibujarla.")

if __name__ == '__main__':
    application = ApplicationBuilder().token('8713996688:AAH0_9hFJrxchmhBYlTuWQ0fIbo9DaBMe_w').build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), procesar_mensaje))
    
    print("El bot está corriendo con motor de IA activado...")
    application.run_polling()