import sqlite3
import pandas as pd

def crear_base_de_datos():
    conn = sqlite3.connect('data/taquigrafia.db')
    
    # Ejemplo para cargar Consonantes
    df_cons = pd.read_csv('data/consonantes.csv')
    df_cons.to_sql('consonantes', conn, if_exists='replace', index=False)
    
    # Repite para vocales y gramálogos...
    print("Base de datos creada exitosamente.")
    conn.close()

if __name__ == "__main__":
    crear_base_de_datos()