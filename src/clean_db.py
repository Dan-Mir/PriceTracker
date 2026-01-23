import sqlite3
import os

db_name = "prezzi.db"

if os.path.exists(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prodotti") # Svuota la tabella
        # cursor.execute("DROP TABLE prodotti") # Alternativa: Cancella proprio la tabella
        conn.commit()
        conn.close()
        print(f"🗑️ Database '{db_name}' svuotato con successo!")
    except Exception as e:
        print(f"❌ Errore durante la pulizia: {e}")
else:
    print("⚠️ Il database non esiste ancora.")