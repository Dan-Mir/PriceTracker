import sqlite3
from datetime import datetime
import os
import hashlib
from typing import List

try:
    from logger import get_logger
    import config
except ImportError:
    from src.logger import get_logger
    from src import config

logger = get_logger(__name__)

class PriceDatabase:
    def __init__(self, db_name=None):
        db_name = db_name or config.DATABASE_NAME
        self.db_path = os.path.abspath(db_name)
        logger.info(f"Database path: {self.db_path}")
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
        logger.warning("insert_product è deprecato, usa upsert_product()")
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
    
    def search_products(self, query: str, supermercato: str = None, limit: int = 10):
        """
        Cerca prodotti per nome (con LIKE) e fuzzy matching
        
        Args:
            query: Testo da cercare
            supermercato: Filtra per supermercato (opzionale)
            limit: Numero massimo risultati
        
        Returns:
            Lista di dict con prodotti trovati
        """
        sql = '''
            SELECT p.nome, p.marca, p.unita_misura, pr.prezzo_attuale, s.nome as supermercato
            FROM prodotti p
            JOIN prezzi pr ON p.id = pr.prodotto_id
            JOIN supermercati s ON pr.supermercato_id = s.id
            WHERE p.nome LIKE ?
              AND pr.id IN (
                  SELECT MAX(id) FROM prezzi GROUP BY prodotto_id, supermercato_id
              )
        '''
        
        params = [f'%{query}%']
        
        if supermercato:
            sql += ' AND s.nome = ?'
            params.append(supermercato)
        
        sql += ' ORDER BY pr.prezzo_attuale ASC LIMIT ?'
        params.append(limit)
        
        cursor = self.conn.execute(sql, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'nome': row[0],
                'marca': row[1],
                'unita_misura': row[2],
                'prezzo': row[3],
                'supermercato': row[4]
            })
        
        return results
    
    def search_products_by_category(self, categories: List[str], limit: int = 20):
        """
        Cerca prodotti per categoria
        
        Args:
            categories: Lista di categorie da cercare
            limit: Numero massimo risultati
        
        Returns:
            Lista di dict con prodotti trovati
        """
        if not categories:
            return []
        
        # Costruisci query con OR per ogni categoria
        category_conditions = ' OR '.join(['p.categoria LIKE ?' for _ in categories])
        
        sql = f'''
            SELECT p.nome, p.marca, p.categoria, p.unita_misura, pr.prezzo_attuale, s.nome as supermercato
            FROM prodotti p
            JOIN prezzi pr ON p.id = pr.prodotto_id
            JOIN supermercati s ON pr.supermercato_id = s.id
            WHERE ({category_conditions})
              AND pr.id IN (
                  SELECT MAX(id) FROM prezzi GROUP BY prodotto_id, supermercato_id
              )
            ORDER BY pr.prezzo_attuale ASC
            LIMIT ?
        '''
        
        params = [f'%{cat}%' for cat in categories]
        params.append(limit)
        
        cursor = self.conn.execute(sql, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'nome': row[0],
                'marca': row[1],
                'categoria': row[2],
                'unita_misura': row[3],
                'prezzo': row[4],
                'supermercato': row[5]
            })
        
        return results
    
    def search_products_enhanced(self, query: str, categories: List[str] = None, limit: int = 20):
        """
        Ricerca avanzata: cerca per nome E per categoria
        
        Args:
            query: Testo da cercare nel nome
            categories: Categorie da includere (opzionale)
            limit: Numero massimo risultati
        
        Returns:
            Lista di dict con prodotti trovati (senza duplicati)
        """
        results = []
        seen = set()  # Per evitare duplicati
        
        # 1. Cerca per nome
        name_results = self.search_products(query, limit=limit)
        for r in name_results:
            key = (r['nome'], r['supermercato'])
            if key not in seen:
                results.append(r)
                seen.add(key)
        
        # 2. Se specificati, cerca anche per categoria
        if categories:
            cat_results = self.search_products_by_category(categories, limit=limit)
            for r in cat_results:
                key = (r['nome'], r['supermercato'])
                if key not in seen and len(results) < limit:
                    results.append(r)
                    seen.add(key)
        
        # Ordina per prezzo
        results.sort(key=lambda x: x['prezzo'])
        
        return results[:limit]
    
    def get_all_supermarkets(self):
        """Ottiene lista di tutti i supermercati nel database"""
        cursor = self.conn.execute("SELECT DISTINCT nome FROM supermercati ORDER BY nome")
        return [row[0] for row in cursor.fetchall()]
    
    def get_products_in_offer(self, min_sconto: float = 5.0, limit: int = 20):
        """
        Ottiene prodotti in offerta
        
        Args:
            min_sconto: Sconto minimo percentuale
            limit: Numero massimo risultati
        
        Returns:
            Lista di tuple (nome, marca, prezzo_listino, prezzo_attuale, sconto, supermercato)
        """
        sql = '''
            SELECT p.nome, p.marca, pr.prezzo_listino, pr.prezzo_attuale, 
                   pr.sconto_percentuale, s.nome as supermercato
            FROM prodotti p
            JOIN prezzi pr ON p.id = pr.prodotto_id
            JOIN supermercati s ON pr.supermercato_id = s.id
            WHERE pr.in_offerta = 1
              AND pr.sconto_percentuale >= ?
              AND pr.id IN (
                  SELECT MAX(id) FROM prezzi GROUP BY prodotto_id, supermercato_id
              )
            ORDER BY pr.sconto_percentuale DESC
            LIMIT ?
        '''
        
        cursor = self.conn.execute(sql, (min_sconto, limit))
        return cursor.fetchall()
    
    def get_price_history(self, nome_prodotto: str, limit: int = 30):
        """
        Ottiene lo storico prezzi di un prodotto
        
        Args:
            nome_prodotto: Nome del prodotto
            limit: Numero massimo rilevazioni
        
        Returns:
            Lista di tuple (prezzo_attuale, data_rilevazione, supermercato)
        """
        sql = '''
            SELECT pr.prezzo_attuale, pr.data_rilevazione, s.nome as supermercato
            FROM prodotti p
            JOIN prezzi pr ON p.id = pr.prodotto_id
            JOIN supermercati s ON pr.supermercato_id = s.id
            WHERE p.nome LIKE ?
            ORDER BY pr.data_rilevazione DESC
            LIMIT ?
        '''
        
        cursor = self.conn.execute(sql, (f'%{nome_prodotto}%', limit))
        return cursor.fetchall()

    def close(self):
        self.conn.close()