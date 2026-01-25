import sqlite3
from datetime import datetime
import os
import hashlib

class PriceDatabase:
    def __init__(self, db_name="prezzi.db"):
        self.db_path = os.path.abspath(db_name)
        print(f"💾 Database path: {self.db_path}")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")  # Abilita foreign keys
        self.create_tables()

    def create_tables(self):
        """Crea le tabelle con la nuova struttura normalizzata"""
        
        # Tabella master prodotti
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS prodotti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                marca TEXT,
                categoria TEXT,
                unita_misura TEXT,
                codice_prodotto TEXT UNIQUE,
                data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_ultimo_update DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabella supermercati
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS supermercati (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                citta TEXT,
                ultimo_scraping DATETIME
            )
        ''')
        
        # Tabella storico prezzi
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS prezzi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prodotto_id INTEGER NOT NULL,
                supermercato_id INTEGER NOT NULL,
                prezzo_listino REAL NOT NULL,
                prezzo_attuale REAL NOT NULL,
                in_offerta BOOLEAN DEFAULT 0,
                sconto_percentuale REAL DEFAULT 0,
                data_rilevazione DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prodotto_id) REFERENCES prodotti(id) ON DELETE CASCADE,
                FOREIGN KEY (supermercato_id) REFERENCES supermercati(id) ON DELETE CASCADE
            )
        ''')
        
        # Indici per performance
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_prezzi_prodotto ON prezzi(prodotto_id)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_prezzi_data ON prezzi(data_rilevazione)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_prodotti_codice ON prodotti(codice_prodotto)')
        
        self.conn.commit()

    def _generate_product_code(self, nome, marca, unita_misura):
        """Genera un codice univoco per identificare lo stesso prodotto"""
        # Normalizza i dati per generare un hash consistente
        nome_norm = nome.lower().strip()
        marca_norm = (marca or "").lower().strip()
        unita_norm = (unita_misura or "").lower().strip()
        
        combined = f"{nome_norm}_{marca_norm}_{unita_norm}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def _get_or_create_supermercato(self, nome_supermercato):
        """Ottiene l'ID del supermercato, creandolo se non esiste"""
        cursor = self.conn.execute(
            "SELECT id FROM supermercati WHERE nome = ?", 
            (nome_supermercato,)
        )
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            cursor = self.conn.execute(
                "INSERT INTO supermercati (nome, ultimo_scraping) VALUES (?, ?)",
                (nome_supermercato, datetime.now())
            )
            self.conn.commit()
            return cursor.lastrowid
    
    def upsert_product(self, nome, marca, prezzo_listino, prezzo_attuale, categoria, supermercato="Eurospin", unita_misura=None):
        """
        Inserisce o aggiorna un prodotto nel DB con logica intelligente:
        - Se il prodotto non esiste, lo crea
        - Se esiste, confronta il prezzo e aggiorna lo storico solo se cambiato
        - Rileva automaticamente se è in offerta
        """
        try:
            # Genera codice univoco prodotto
            codice = self._generate_product_code(nome, marca, unita_misura)
            supermercato_id = self._get_or_create_supermercato(supermercato)
            
            # Cerca se il prodotto esiste già
            cursor = self.conn.execute(
                "SELECT id FROM prodotti WHERE codice_prodotto = ?",
                (codice,)
            )
            result = cursor.fetchone()
            
            if result:
                # Prodotto esiste, aggiorna timestamp
                prodotto_id = result[0]
                self.conn.execute(
                    "UPDATE prodotti SET data_ultimo_update = ? WHERE id = ?",
                    (datetime.now(), prodotto_id)
                )
            else:
                # Prodotto nuovo, inseriscilo
                cursor = self.conn.execute('''
                    INSERT INTO prodotti (nome, marca, categoria, unita_misura, codice_prodotto)
                    VALUES (?, ?, ?, ?, ?)
                ''', (nome, marca, categoria, unita_misura, codice))
                prodotto_id = cursor.lastrowid
            
            # Controlla l'ultimo prezzo registrato per questo prodotto in questo supermercato
            cursor = self.conn.execute('''
                SELECT prezzo_attuale, data_rilevazione 
                FROM prezzi 
                WHERE prodotto_id = ? AND supermercato_id = ?
                ORDER BY data_rilevazione DESC LIMIT 1
            ''', (prodotto_id, supermercato_id))
            
            ultimo_prezzo = cursor.fetchone()
            
            # Inserisci nuovo record solo se:
            # 1. Non c'è storico precedente, OPPURE
            # 2. Il prezzo è cambiato, OPPURE
            # 3. È passato più di 1 giorno dall'ultima rilevazione
            inserisci_record = False
            
            if not ultimo_prezzo:
                inserisci_record = True
            else:
                prezzo_precedente = ultimo_prezzo[0]
                data_precedente = datetime.fromisoformat(ultimo_prezzo[1])
                ore_trascorse = (datetime.now() - data_precedente).total_seconds() / 3600
                
                if abs(prezzo_attuale - prezzo_precedente) > 0.01 or ore_trascorse > 24:
                    inserisci_record = True
            
            if inserisci_record:
                # Calcola se è in offerta
                in_offerta = prezzo_attuale < prezzo_listino
                sconto_pct = ((prezzo_listino - prezzo_attuale) / prezzo_listino * 100) if in_offerta else 0
                
                self.conn.execute('''
                    INSERT INTO prezzi (prodotto_id, supermercato_id, prezzo_listino, prezzo_attuale, 
                                       in_offerta, sconto_percentuale, data_rilevazione)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (prodotto_id, supermercato_id, prezzo_listino, prezzo_attuale, 
                      in_offerta, sconto_pct, datetime.now()))
            
            self.conn.commit()
            return prodotto_id
            
        except Exception as e:
            print(f"   ❌ ERRORE SQL upsert: {e}")
            return None
    
    def insert_product(self, nome, marca, p_listino, p_offerta, categoria, supermercato="Eurospin"):
        """DEPRECATO: Usa upsert_product(). Mantenuto per backward compatibility"""
        return self.upsert_product(nome, marca, p_listino, p_offerta, categoria, supermercato)
    
    def get_products_in_offer(self, supermercato=None, min_sconto=0):
        """Ottiene prodotti attualmente in offerta"""
        query = '''
            SELECT p.nome, p.marca, pr.prezzo_listino, pr.prezzo_attuale, 
                   pr.sconto_percentuale, s.nome as supermercato, pr.data_rilevazione
            FROM prezzi pr
            JOIN prodotti p ON pr.prodotto_id = p.id
            JOIN supermercati s ON pr.supermercato_id = s.id
            WHERE pr.in_offerta = 1 
              AND pr.sconto_percentuale >= ?
              AND pr.id IN (
                  SELECT MAX(id) FROM prezzi GROUP BY prodotto_id, supermercato_id
              )
        '''
        params = [min_sconto]
        
        if supermercato:
            query += " AND s.nome = ?"
            params.append(supermercato)
        
        query += " ORDER BY pr.sconto_percentuale DESC"
        
        cursor = self.conn.execute(query, params)
        return cursor.fetchall()
    
    def get_price_history(self, prodotto_nome, supermercato=None):
        """Ottiene lo storico prezzi di un prodotto"""
        query = '''
            SELECT pr.prezzo_attuale, pr.data_rilevazione, s.nome as supermercato
            FROM prezzi pr
            JOIN prodotti p ON pr.prodotto_id = p.id
            JOIN supermercati s ON pr.supermercato_id = s.id
            WHERE p.nome LIKE ?
        '''
        params = [f"%{prodotto_nome}%"]
        
        if supermercato:
            query += " AND s.nome = ?"
            params.append(supermercato)
        
        query += " ORDER BY pr.data_rilevazione ASC"
        
        cursor = self.conn.execute(query, params)
        return cursor.fetchall()
    
    def get_stats(self):
        """Statistiche generali sul database"""
        stats = {}
        
        cursor = self.conn.execute("SELECT COUNT(*) FROM prodotti")
        stats['totale_prodotti'] = cursor.fetchone()[0]
        
        cursor = self.conn.execute("SELECT COUNT(*) FROM supermercati")
        stats['totale_supermercati'] = cursor.fetchone()[0]
        
        cursor = self.conn.execute('''
            SELECT COUNT(*) FROM prezzi 
            WHERE in_offerta = 1 
              AND id IN (SELECT MAX(id) FROM prezzi GROUP BY prodotto_id, supermercato_id)
        ''')
        stats['prodotti_in_offerta'] = cursor.fetchone()[0]
        
        cursor = self.conn.execute("SELECT COUNT(*) FROM prezzi")
        stats['totale_rilevazioni'] = cursor.fetchone()[0]
        
        return stats
    
    def update_supermercato_scraping(self, nome_supermercato):
        """Aggiorna il timestamp dell'ultimo scraping"""
        self.conn.execute(
            "UPDATE supermercati SET ultimo_scraping = ? WHERE nome = ?",
            (datetime.now(), nome_supermercato)
        )
        self.conn.commit()

    def close(self):
        self.conn.close()