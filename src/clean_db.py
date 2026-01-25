import sqlite3
import os

db_name = "prezzi.db"

if os.path.exists(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        # Ottieni tutte le tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # Svuota ogni tabella
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DELETE FROM {table_name}")
            print(f"  ✓ Tabella '{table_name}' svuotata")
        # cursor.execute("DROP TABLE prodotti") # Alternativa: Cancella proprio la tabella
        conn.commit()
        conn.close()
        print(f"🗑️ Database '{db_name}' svuotato con successo!")
    except Exception as e:
        print(f"❌ Errore durante la pulizia: {e}")
else:
    print("⚠️ Il database non esiste ancora.")