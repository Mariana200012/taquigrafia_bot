import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Configuración básica de logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu bot de taquigrafía. Escribe una palabra y generaré el trazo.")

async def procesar_palabra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    
    # Aquí irá la lógica de dibujo que planeamos antes
    await update.message.reply_text(f"Procesando la palabra: {texto}...")
    # Por ahora solo responde, luego enviaremos la imagen generada con Pillow

if __name__ == '__main__':
    application = ApplicationBuilder().token('TU_TOKEN_AQUÍ').build()
    
    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), procesar_palabra)
    
    application.add_handler(start_handler)
    application.add_handler(msg_handler)
    
    application.run_polling()