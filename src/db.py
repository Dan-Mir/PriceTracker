import sqlite3
from datetime import datetime
import os

class PriceDatabase:
    def __init__(self, db_name="prezzi.db"):
        # Usiamo path assoluto per evitare confusione tra cartelle
        self.db_path = os.path.abspath(db_name)
        print(f"💾 Database path: {self.db_path}")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS prodotti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            marca TEXT,
            prezzo_listino REAL,
            prezzo_offerta REAL,
            unita_misura TEXT,
            categoria TEXT,
            supermercato TEXT,
            data_aggiornamento DATETIME
        )
        '''
        self.conn.execute(query)
        self.conn.commit()

    def insert_product(self, nome, marca, p_listino, p_offerta, categoria, supermercato="Eurospin"):
        try:
            query = '''
            INSERT INTO prodotti (nome, marca, prezzo_listino, prezzo_offerta, categoria, supermercato, data_aggiornamento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            self.conn.execute(query, (nome, marca, p_listino, p_offerta, categoria, supermercato, datetime.now()))
            self.conn.commit()
            # Decommenta questa riga se vuoi vedere ogni singolo inserimento in console
            # print(f"   [DB OK] Salvato: {nome}") 
        except Exception as e:
            print(f"   ❌ ERRORE SQL: {e}")

    def close(self):
        self.conn.close()