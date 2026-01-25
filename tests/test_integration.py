"""
Test di integrazione per il sistema completo
"""
import unittest
import os
import sys
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from db import PriceDatabase


class TestIntegrationWorkflow(unittest.TestCase):
    """Test workflow completo del sistema"""
    
    def setUp(self):
        self.test_db = "test_integration.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = PriceDatabase(self.test_db)
    
    def tearDown(self):
        self.db.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_complete_workflow(self):
        """Test workflow completo: inserimento → aggiornamento → query offerte"""
        
        # 1. Inserimento iniziale prodotti
        self.db.upsert_product("Pasta Penne", "Barilla", 1.50, 1.50, "Dispensa", "Eurospin", "500g")
        self.db.upsert_product("Latte", "Parmalat", 1.20, 1.20, "Latticini", "Eurospin", "1L")
        self.db.upsert_product("Olio EVO", "DeCecco", 8.50, 8.50, "Condimenti", "Eurospin", "1L")
        
        # Verifica inserimento
        stats = self.db.get_stats()
        self.assertEqual(stats['totale_prodotti'], 3)
        self.assertEqual(stats['totale_rilevazioni'], 3)
        self.assertEqual(stats['prodotti_in_offerta'], 0)
        
        # 2. Simulazione aggiornamento: alcuni prodotti vanno in offerta
        self.db.upsert_product("Pasta Penne", "Barilla", 1.50, 0.99, "Dispensa", "Eurospin", "500g")
        self.db.upsert_product("Olio EVO", "DeCecco", 8.50, 5.99, "Condimenti", "Eurospin", "1L")
        
        # Verifica aggiornamento
        stats = self.db.get_stats()
        self.assertEqual(stats['totale_prodotti'], 3)  # Sempre 3 prodotti
        self.assertEqual(stats['totale_rilevazioni'], 5)  # 3 iniziali + 2 aggiornamenti
        self.assertEqual(stats['prodotti_in_offerta'], 2)  # Pasta e Olio in offerta
        
        # 3. Query offerte
        offerte = self.db.get_products_in_offer(min_sconto=10)
        self.assertEqual(len(offerte), 2)
        
        # Verifica ordine (per sconto decrescente)
        nomi_offerte = [o[0] for o in offerte]
        self.assertIn("Pasta Penne", nomi_offerte)
        self.assertIn("Olio EVO", nomi_offerte)
        
        # 4. Query storico
        storico_pasta = self.db.get_price_history("Pasta")
        self.assertEqual(len(storico_pasta), 2)
        
        # Prezzi devono essere in ordine cronologico
        self.assertEqual(storico_pasta[0][0], 1.50)  # Prezzo iniziale
        self.assertEqual(storico_pasta[1][0], 0.99)  # Prezzo scontato
    
    def test_multi_supermercato(self):
        """Test gestione multipli supermercati"""
        
        # Stesso prodotto in supermercati diversi
        self.db.upsert_product("Pasta", "Barilla", 1.50, 1.50, "Dispensa", "Eurospin", "500g")
        self.db.upsert_product("Pasta", "Barilla", 1.50, 1.30, "Dispensa", "Lidl", "500g")
        self.db.upsert_product("Pasta", "Barilla", 1.50, 1.40, "Dispensa", "Conad", "500g")
        
        stats = self.db.get_stats()
        self.assertEqual(stats['totale_prodotti'], 1)  # Un solo prodotto
        self.assertEqual(stats['totale_supermercati'], 3)  # Tre supermercati
        self.assertEqual(stats['totale_rilevazioni'], 3)  # 3 rilevazioni (una per super)
        
        # Verifica offerte per supermercato specifico
        offerte_lidl = self.db.get_products_in_offer(supermercato="Lidl")
        self.assertEqual(len(offerte_lidl), 1)
        self.assertEqual(offerte_lidl[0][5], "Lidl")  # Nome supermercato


class TestDataConsistency(unittest.TestCase):
    """Test consistenza dati e edge cases"""
    
    def setUp(self):
        self.test_db = "test_consistency.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = PriceDatabase(self.test_db)
    
    def tearDown(self):
        self.db.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_zero_price_handling(self):
        """Test gestione prezzi a zero"""
        prodotto_id = self.db.upsert_product("Test", "", 0.0, 0.0, "Cat", "Super")
        self.assertIsNotNone(prodotto_id)
    
    def test_empty_strings_handling(self):
        """Test gestione stringhe vuote"""
        prodotto_id = self.db.upsert_product("", "", 1.0, 1.0, "", "")
        self.assertIsNotNone(prodotto_id)
    
    def test_same_product_different_sizes(self):
        """Test stesso prodotto con formati diversi"""
        id1 = self.db.upsert_product("Latte", "Parmalat", 1.20, 1.20, "Latticini", "Eurospin", "1L")
        id2 = self.db.upsert_product("Latte", "Parmalat", 0.60, 0.60, "Latticini", "Eurospin", "500ml")
        
        # Devono essere prodotti diversi (formato diverso)
        stats = self.db.get_stats()
        self.assertEqual(stats['totale_prodotti'], 2)


if __name__ == '__main__':
    unittest.main()
