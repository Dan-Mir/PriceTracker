
import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src import config

def show_stats():
    db_path = config.DATABASE_NAME
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== DATABASE STATISTICS ===")
    
    # Total products
    cursor.execute("SELECT COUNT(*) FROM prodotti")
    total = cursor.fetchone()[0]
    print(f"Total Products: {total}")

    # Per Supermarket
    print("\nProducts per Supermarket:")
    cursor.execute("""
        SELECT s.nome, COUNT(p.id) 
        FROM prodotti p 
        JOIN prezzi pr ON p.id = pr.prodotto_id 
        JOIN supermercati s ON pr.supermercato_id = s.id 
        WHERE pr.id IN (SELECT MAX(id) FROM prezzi GROUP BY prodotto_id, supermercato_id)
        GROUP BY s.nome
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Per Category (Castoro)
    print("\nTop 10 Categories:")
    cursor.execute("SELECT categoria, COUNT(*) FROM prodotti GROUP BY categoria ORDER BY COUNT(*) DESC LIMIT 10")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()

if __name__ == "__main__":
    show_stats()
