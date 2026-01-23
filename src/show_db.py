import sqlite3
from pathlib import Path

def show_database():
    """Esegue query sul database prezzi.db"""
    
    # Percorso del database
    db_path = Path(__file__).parent / "prezzi.db"
    
    if not db_path.exists():
        print(f"Database non trovato: {db_path}")
        return
    
    # Connessione al database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Mostra tutte le tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tabelle nel database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "="*50 + "\n")
        
        q = input("Inserisci la query SQL da eseguire (o 'ctrl + C' per uscire): ")
        cursor.execute(q)
        results = cursor.fetchall()
        for row in results:
            print(row)
        
    
    except sqlite3.Error as e:
        print(f"Errore: {e}")
    except KeyboardInterrupt:
        print("\nOperazione interrotta dall'utente.")
    
    finally:
        conn.close()

if __name__ == "__main__":
    show_database()