import sqlite3
import pandas as pd
import os

def crear_base_de_datos():
    # Asegúrate de que la carpeta data existe
    if not os.path.exists('data'):
        os.makedirs('data')

    conn = sqlite3.connect('data/taquigrafia.db')
    
    # 1. Cargar Consonantes
    df_cons = pd.read_csv('data/consonantes.csv')
    df_cons.to_sql('consonantes', conn, if_exists='replace', index=False)
    
    # 2. Cargar Vocales
    df_voc = pd.read_csv('data/vocales_posicion.csv')
    df_voc.to_sql('vocales', conn, if_exists='replace', index=False)

    # 3. Cargar Gramálogos (ESTA ES LA QUE TE FALTA)
    df_gram = pd.read_csv('data/gramalogos.csv')
    df_gram.to_sql('gramalogos', conn, if_exists='replace', index=False)

    # 4. Cargar Signos/Puntuación
    df_sig = pd.read_csv('data/signos.csv')
    df_sig.to_sql('signos', conn, if_exists='replace', index=False)
    
    print("Base de datos creada exitosamente con todas las tablas.")
    conn.close()

if __name__ == "__main__":
    crear_base_de_datos()