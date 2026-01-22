import sqlite3
from datetime import datetime

class PriceDatabase:
    def __init__(self, db_name="prezzi.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS prodotti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            marca TEXT,
            prezzo_listino REAL,
            prezzo_offerta REAL,
            supermercato TEXT,
            data_aggiornamento DATETIME
        )
        '''
        self.conn.execute(query)
        self.conn.commit()

    def insert_product(self, nome, marca, p_listino, p_offerta, supermercato):
        query = '''
        INSERT INTO prodotti (nome, marca, prezzo_listino, prezzo_offerta, supermercato, data_aggiornamento)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.conn.execute(query, (nome, marca, p_listino, p_offerta, supermercato, datetime.now()))
        self.conn.commit()

    def get_all_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM prodotti")
        return cursor.fetchall()
    
    def close(self):
        self.conn.close()