"""
Test paginazione Castoro - scraping di una sola categoria con tutte le pagine
"""
from src.castoro.castoro_parser import CastoroParser

# Test su categoria pasta (dovrebbe avere molti prodotti)
parser = CastoroParser()

try:
    print("🔍 Test scraping con paginazione su: pasta-riso-e-farine/pasta\n")
    
    # Inizializza driver e carica homepage
    parser._setup_driver()
    parser.driver.get("https://www.castoro.shop")
    import time
    time.sleep(5)
    parser._remove_cookie_banner()
    
    # Test scraping
    products = parser._scrape_category_by_url("/category/pasta-riso-e-farine/pasta")
    
    print(f"\n\n✅ RISULTATO:")
    print(f"   Prodotti trovati: {len(products)}")
    
    if products:
        print(f"\n📦 Primi 5 prodotti:")
        for i, p in enumerate(products[:5], 1):
            print(f"   {i}. {p['nome']} - €{p['prezzo']}")
    
finally:
    parser.close()
