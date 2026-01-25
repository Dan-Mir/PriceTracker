"""
Test suite per il modulo database (db.py)
Tests per funzionalità CRUD, upsert, query offerte, storico prezzi
"""
import unittest
import sqlite3
import os
import sys
from datetime import datetime, timedelta

# Aggiungi src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from db import PriceDatabase


class TestPriceDatabase(unittest.TestCase):
    """Test per la classe PriceDatabase"""
    
    def setUp(self):
        """Setup: crea un database di test temporaneo"""
        self.test_db = "test_prezzi.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = PriceDatabase(self.test_db)
    
    def tearDown(self):
        """Cleanup: rimuove il database di test"""
        self.db.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_create_tables(self):
        """Test creazione tabelle"""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Verifica esistenza tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn('prodotti', tables)
        self.assertIn('prezzi', tables)
        self.assertIn('supermercati', tables)
        
        conn.close()
    
    def test_generate_product_code(self):
        """Test generazione codice prodotto univoco"""
        code1 = self.db._generate_product_code("Pasta", "Barilla", "500g")
        code2 = self.db._generate_product_code("pasta", "barilla", "500g")
        code3 = self.db._generate_product_code("Pasta", "DeCecco", "500g")
        
        # Stesso prodotto (case insensitive) = stesso codice
        self.assertEqual(code1, code2)
        
        # Marca diversa = codice diverso
        self.assertNotEqual(code1, code3)
        
        # Codice deve essere lungo 16 caratteri
        self.assertEqual(len(code1), 16)
    
    def test_get_or_create_supermercato(self):
        """Test creazione/recupero supermercato"""
        # Prima chiamata: crea il supermercato
        id1 = self.db._get_or_create_supermercato("Eurospin")
        self.assertIsNotNone(id1)
        
        # Seconda chiamata: recupera lo stesso ID
        id2 = self.db._get_or_create_supermercato("Eurospin")
        self.assertEqual(id1, id2)
        
        # Supermercato diverso = ID diverso
        id3 = self.db._get_or_create_supermercato("Lidl")
        self.assertNotEqual(id1, id3)
    
    def test_upsert_product_new(self):
        """Test inserimento nuovo prodotto"""
        prodotto_id = self.db.upsert_product(
            nome="Latte Intero",
            marca="Centrale",
            prezzo_listino=1.20,
            prezzo_attuale=1.20,
            categoria="Latticini",
            supermercato="Eurospin",
            unita_misura="1L"
        )
        
        self.assertIsNotNone(prodotto_id)
        
        # Verifica che sia stato creato
        stats = self.db.get_stats()
        self.assertEqual(stats['totale_prodotti'], 1)
        self.assertEqual(stats['totale_rilevazioni'], 1)
    
    def test_upsert_product_duplicate(self):
        """Test che prodotto duplicato non viene reinserito"""
        # Inserimento 1
        id1 = self.db.upsert_product(
            nome="Pasta",
            marca="Barilla",
            prezzo_listino=1.50,
            prezzo_attuale=1.50,
            categoria="Dispensa",
            supermercato="Eurospin",
            unita_misura="500g"
        )
        
        # Inserimento 2 (stesso prodotto, stesso prezzo, entro 24h)
        id2 = self.db.upsert_product(
            nome="Pasta",
            marca="Barilla",
            prezzo_listino=1.50,
            prezzo_attuale=1.50,
            categoria="Dispensa",
            supermercato="Eurospin",
            unita_misura="500g"
        )
        
        stats = self.db.get_stats()
        self.assertEqual(stats['totale_prodotti'], 1)  # Un solo prodotto
        self.assertEqual(stats['totale_rilevazioni'], 1)  # Una sola rilevazione (prezzo non cambiato)
    
    def test_upsert_product_price_change(self):
        """Test che cambio prezzo crea nuova rilevazione"""
        # Inserimento iniziale
        self.db.upsert_product(
            nome="Olio",
            marca="DeCecco",
            prezzo_listino=8.50,
            prezzo_attuale=8.50,
            categoria="Condimenti",
            supermercato="Eurospin",
            unita_misura="1L"
        )
        
        # Cambio prezzo
        self.db.upsert_product(
            nome="Olio",
            marca="DeCecco",
            prezzo_listino=8.50,
            prezzo_attuale=5.99,  # SCONTO
            categoria="Condimenti",
            supermercato="Eurospin",
            unita_misura="1L"
        )
        
        stats = self.db.get_stats()
        self.assertEqual(stats['totale_prodotti'], 1)  # Un solo prodotto
        self.assertEqual(stats['totale_rilevazioni'], 2)  # Due rilevazioni (prezzo cambiato)
        self.assertEqual(stats['prodotti_in_offerta'], 1)  # In offerta
    
    def test_detect_offerta(self):
        """Test rilevamento offerta"""
        self.db.upsert_product(
            nome="Caffè",
            marca="Lavazza",
            prezzo_listino=5.00,
            prezzo_attuale=3.99,
            categoria="Bevande",
            supermercato="Eurospin",
            unita_misura="250g"
        )
        
        offerte = self.db.get_products_in_offer(min_sconto=0)
        self.assertEqual(len(offerte), 1)
        
        # Verifica percentuale sconto
        _, _, prezzo_listino, prezzo_attuale, sconto_pct, _, _ = offerte[0]
        expected_sconto = ((5.00 - 3.99) / 5.00) * 100
        self.assertAlmostEqual(sconto_pct, expected_sconto, places=1)
    
    def test_get_products_in_offer_filter(self):
        """Test filtro offerte per sconto minimo"""
        # Prodotto 1: sconto 10%
        self.db.upsert_product("P1", "", 10.00, 9.00, "Cat", "Eurospin")
        
        # Prodotto 2: sconto 30%
        self.db.upsert_product("P2", "", 10.00, 7.00, "Cat", "Eurospin")
        
        # Prodotto 3: sconto 5%
        self.db.upsert_product("P3", "", 10.00, 9.50, "Cat", "Eurospin")
        
        # Filtro >= 20%
        offerte = self.db.get_products_in_offer(min_sconto=20)
        self.assertEqual(len(offerte), 1)  # Solo P2
    
    def test_get_price_history(self):
        """Test recupero storico prezzi"""
        # Inserimento 1
        self.db.upsert_product("Pasta", "Barilla", 1.50, 1.50, "Dispensa", "Eurospin", "500g")
        
        # Inserimento 2 (prezzo cambiato)
        self.db.upsert_product("Pasta", "Barilla", 1.50, 0.99, "Dispensa", "Eurospin", "500g")
        
        storico = self.db.get_price_history("Pasta")
        self.assertEqual(len(storico), 2)
        
        # Verifica ordine cronologico
        prezzo1, data1, _ = storico[0]
        prezzo2, data2, _ = storico[1]
        
        self.assertEqual(prezzo1, 1.50)
        self.assertEqual(prezzo2, 0.99)
        self.assertLess(data1, data2)  # Primo record più vecchio
    
    def test_get_stats(self):
        """Test statistiche database"""
        stats = self.db.get_stats()
        
        # Verifica campi presenti
        self.assertIn('totale_prodotti', stats)
        self.assertIn('totale_supermercati', stats)
        self.assertIn('totale_rilevazioni', stats)
        self.assertIn('prodotti_in_offerta', stats)
        
        # DB vuoto
        self.assertEqual(stats['totale_prodotti'], 0)
    
    def test_backward_compatibility_insert_product(self):
        """Test backward compatibility con vecchio insert_product"""
        # Il vecchio metodo deve ancora funzionare
        id = self.db.insert_product("Test", "Marca", 1.00, 0.90, "Cat", "Eurospin")
        self.assertIsNotNone(id)
        
        stats = self.db.get_stats()
        self.assertEqual(stats['totale_prodotti'], 1)


class TestDatabaseIntegrity(unittest.TestCase):
    """Test integrità referenziale e vincoli database"""
    
    def setUp(self):
        self.test_db = "test_integrity.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = PriceDatabase(self.test_db)
    
    def tearDown(self):
        self.db.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_foreign_key_enabled(self):
        """Test che le foreign key siano abilitate"""
        # Le foreign keys sono abilitate a livello di connessione in PriceDatabase
        # Verifichiamo che la connessione del db le abbia attive
        cursor = self.db.conn.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        
        self.assertEqual(result[0], 1)  # Foreign keys ON
    
    def test_unique_product_code(self):
        """Test vincolo univocità codice prodotto"""
        self.db.upsert_product("Prodotto", "Marca", 1.0, 1.0, "Cat", "Super", "100g")
        
        # Stesso prodotto non deve creare duplicati
        self.db.upsert_product("Prodotto", "Marca", 1.0, 1.0, "Cat", "Super", "100g")
        
        stats = self.db.get_stats()
        self.assertEqual(stats['totale_prodotti'], 1)


if __name__ == '__main__':
    unittest.main()
