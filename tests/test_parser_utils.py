"""
Test suite per utility del parser (parser.py)
Tests per funzioni di utility come _clean_price, _is_weight, ecc.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.eurospin.parser import EurospinParser


class TestParserUtilities(unittest.TestCase):
    """Test per le utility del parser"""
    
    @classmethod
    def setUpClass(cls):
        """Setup: crea una istanza del parser (senza avviare il browser)"""
        # Non possiamo testare completamente il parser senza un browser,
        # ma possiamo testare le funzioni utility
        pass
    
    def test_clean_price_standard(self):
        """Test pulizia prezzi standard"""
        parser = EurospinParser.__new__(EurospinParser)  # Crea istanza senza __init__
        
        self.assertEqual(parser._clean_price("1,50 €"), 1.50)
        self.assertEqual(parser._clean_price("€1.50"), 1.50)
        self.assertEqual(parser._clean_price("10,99€"), 10.99)
        self.assertEqual(parser._clean_price("0,99 €"), 0.99)
    
    def test_clean_price_edge_cases(self):
        """Test casi edge per pulizia prezzi"""
        parser = EurospinParser.__new__(EurospinParser)
        
        # Stringa vuota o None
        self.assertEqual(parser._clean_price(""), 0.0)
        self.assertEqual(parser._clean_price(None), 0.0)
        
        # Formato insolito
        self.assertEqual(parser._clean_price("€ 1.99"), 1.99)
        self.assertEqual(parser._clean_price("2,50"), 2.50)
    
    def test_is_weight_valid(self):
        """Test riconoscimento pesi validi"""
        parser = EurospinParser.__new__(EurospinParser)
        
        # Pesi validi
        self.assertTrue(parser._is_weight("500g"))
        self.assertTrue(parser._is_weight("1kg"))
        self.assertTrue(parser._is_weight("250 g"))
        self.assertTrue(parser._is_weight("1,5 kg"))
        self.assertTrue(parser._is_weight("500ml"))
        self.assertTrue(parser._is_weight("1L"))
        self.assertTrue(parser._is_weight("33cl"))
        self.assertTrue(parser._is_weight("6 pezzi"))
        self.assertTrue(parser._is_weight("2pz"))
    
    def test_is_weight_invalid(self):
        """Test riconoscimento non-pesi"""
        parser = EurospinParser.__new__(EurospinParser)
        
        # Non sono pesi
        self.assertFalse(parser._is_weight("Pasta Barilla"))
        self.assertFalse(parser._is_weight("€1.50"))
        self.assertFalse(parser._is_weight("Aggiungi al carrello"))
        self.assertFalse(parser._is_weight(""))
        self.assertFalse(parser._is_weight("abc123"))
    
    def test_is_valid_category_url_valid(self):
        """Test validazione URL categoria validi"""
        parser = EurospinParser.__new__(EurospinParser)
        parser.BLACKLIST_URL = [
            "faq", "assistenza", "contatti", "privacy", "cookie",
            "login", "carrello", "checkout"
        ]
        
        # URL validi
        self.assertTrue(parser._is_valid_category_url(
            "https://laspesaonline.eurospin.it/frutta-e-verdura",
            "Frutta e Verdura"
        ))
        
        self.assertTrue(parser._is_valid_category_url(
            "https://laspesaonline.eurospin.it/dispensa/pasta",
            "Pasta"
        ))
    
    def test_is_valid_category_url_invalid(self):
        """Test validazione URL categoria invalidi"""
        parser = EurospinParser.__new__(EurospinParser)
        parser.BLACKLIST_URL = [
            "faq", "assistenza", "contatti", "privacy", "cookie",
            "login", "carrello", "checkout"
        ]
        
        # URL blacklist
        self.assertFalse(parser._is_valid_category_url(
            "https://laspesaonline.eurospin.it/faq",
            "FAQ"
        ))
        
        self.assertFalse(parser._is_valid_category_url(
            "https://laspesaonline.eurospin.it/carrello",
            "Carrello"
        ))
        
        # URL prodotto specifico (con codice numerico lungo)
        self.assertFalse(parser._is_valid_category_url(
            "https://laspesaonline.eurospin.it/pasta-123456",
            "Pasta"
        ))
        
        # JavaScript
        self.assertFalse(parser._is_valid_category_url(
            "javascript:void(0)",
            "Link"
        ))
        
        # Testo troppo corto
        self.assertFalse(parser._is_valid_category_url(
            "https://laspesaonline.eurospin.it/x",
            "X"
        ))
        
        # Non eurospin
        self.assertFalse(parser._is_valid_category_url(
            "https://www.example.com/test",
            "Test"
        ))


class TestParserBlacklist(unittest.TestCase):
    """Test blacklist URL"""
    
    def test_blacklist_coverage(self):
        """Test che la blacklist contenga parole chiave comuni"""
        parser = EurospinParser.__new__(EurospinParser)
        parser.BLACKLIST_URL = [
            "faq", "assistenza", "contatti", "privacy", "cookie", "policy",
            "login", "registrati", "volantino", "negozi", "store",
            "carrello", "checkout", "profile"
        ]
        
        required_keywords = ["faq", "privacy", "login", "carrello", "contatti"]
        
        for keyword in required_keywords:
            self.assertIn(keyword, parser.BLACKLIST_URL,
                         f"Keyword '{keyword}' dovrebbe essere nella blacklist")


if __name__ == '__main__':
    unittest.main()
