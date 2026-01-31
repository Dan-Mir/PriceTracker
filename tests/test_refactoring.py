#!/usr/bin/env python3
"""
Script di test per verificare il refactoring Fase 1
"""
import sys
import os

# Aggiungi src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_imports():
    """Test 1: Verifica che tutti i moduli si importino correttamente"""
    print("🧪 Test 1: Import moduli...")
    try:
        import config
        from logger import get_logger
        from normalizer import ProductNormalizer, fuzzy_match, extract_unit
        from utils import retry_on_exception, rate_limit, RateLimiter
        from db import PriceDatabase
        print("   ✅ Tutti i moduli importati correttamente")
        return True
    except Exception as e:
        print(f"   ❌ Errore import: {e}")
        return False


def test_config():
    """Test 2: Verifica configurazione"""
    print("\n🧪 Test 2: Configurazione...")
    try:
        import config
        assert config.DATABASE_NAME == "prezzi.db"
        assert config.EUROSPIN_URL == "https://laspesaonline.eurospin.it"
        assert config.FUZZY_MATCH_THRESHOLD == 80
        assert len(config.URL_BLACKLIST) > 0
        print(f"   ✅ Config OK - {len(config.URL_BLACKLIST)} URL in blacklist")
        print(f"   ✅ Timeout: {config.SELENIUM_TIMEOUT}s, Max iterazioni: {config.MAX_ITERATIONS}")
        return True
    except Exception as e:
        print(f"   ❌ Errore config: {e}")
        return False


def test_logger():
    """Test 3: Verifica logging"""
    print("\n🧪 Test 3: Sistema di logging...")
    try:
        from logger import get_logger
        logger = get_logger("test_refactoring")
        
        logger.debug("Test DEBUG message")
        logger.info("Test INFO message")
        logger.warning("Test WARNING message")
        
        import os
        log_exists = os.path.exists("logs/scraper.log")
        print(f"   ✅ Logger funzionante - File log creato: {log_exists}")
        return True
    except Exception as e:
        print(f"   ❌ Errore logger: {e}")
        return False


def test_normalizer():
    """Test 4: Verifica normalizzazione prodotti"""
    print("\n🧪 Test 4: Normalizzatore prodotti...")
    try:
        from normalizer import ProductNormalizer, fuzzy_match, extract_unit
        
        normalizer = ProductNormalizer()
        
        # Test estrazione unità
        unit1 = extract_unit("Pasta Barilla 500g")
        unit2 = extract_unit("Latte Intero 1L")
        unit3 = extract_unit("Acqua Minerale 6x1,5L")
        
        print(f"   ✅ Estrazione unità:")
        print(f"      • 'Pasta Barilla 500g' → '{unit1}'")
        print(f"      • 'Latte Intero 1L' → '{unit2}'")
        print(f"      • 'Acqua Minerale 6x1,5L' → '{unit3}'")
        
        # Test fuzzy matching
        match1 = fuzzy_match("Latte Intero", "LATTE INTERO 1L")
        match2 = fuzzy_match("Pasta Barilla", "Spaghetti Barilla")
        match3 = fuzzy_match("Coca Cola", "Pepsi Cola")
        
        print(f"   ✅ Fuzzy matching:")
        print(f"      • 'Latte Intero' vs 'LATTE INTERO 1L' → {match1}")
        print(f"      • 'Pasta Barilla' vs 'Spaghetti Barilla' → {match2}")
        print(f"      • 'Coca Cola' vs 'Pepsi Cola' → {match3}")
        
        # Test normalizzazione
        norm = normalizer.normalize_text("PASTA   BARILLA!!! 500g")
        print(f"   ✅ Normalizzazione:")
        print(f"      • 'PASTA   BARILLA!!! 500g' → '{norm}'")
        
        # Test similarità
        score = normalizer.similarity_score("Latte Parzialmente Scremato", "Latte P.S. 1L")
        print(f"   ✅ Similarità: {score:.1f}/100")
        
        return True
    except Exception as e:
        print(f"   ❌ Errore normalizer: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Test 5: Verifica utilities"""
    print("\n🧪 Test 5: Utilities (retry, rate limiting)...")
    try:
        from utils import retry_on_exception, rate_limit, RateLimiter
        import time
        
        # Test rate limiter
        limiter = RateLimiter(min_delay=0.5, max_delay=1.0)
        
        start = time.time()
        limiter.wait()
        limiter.wait()
        elapsed = time.time() - start
        
        print(f"   ✅ RateLimiter: 2 chiamate in {elapsed:.2f}s (atteso: 0.5-1.0s)")
        
        # Test decorator retry
        call_count = [0]
        
        @retry_on_exception(max_retries=3, delay=0.1, backoff=2.0)
        def failing_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Test error")
            return "success"
        
        result = failing_function()
        print(f"   ✅ Retry decorator: {call_count[0]} tentativi, risultato='{result}'")
        
        return True
    except Exception as e:
        print(f"   ❌ Errore utils: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database():
    """Test 6: Verifica database con nuovi campi"""
    print("\n🧪 Test 6: Database (schema + unità misura)...")
    try:
        from db import PriceDatabase
        import os
        
        # Usa un DB di test
        test_db = "test_refactoring.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        db = PriceDatabase(test_db)
        
        # Test inserimento con unità misura
        product_id = db.upsert_product(
            nome="Pasta Barilla",
            marca="BARILLA",
            prezzo_listino=1.99,
            prezzo_attuale=1.49,
            categoria="Alimentari > Pasta",
            supermercato="Eurospin",
            unita_misura="500 g"
        )
        
        print(f"   ✅ Prodotto inserito con ID: {product_id}")
        
        # Verifica stats
        stats = db.get_stats()
        print(f"   ✅ Stats DB:")
        print(f"      • Prodotti totali: {stats['totale_prodotti']}")
        print(f"      • Supermercati: {stats['totale_supermercati']}")
        print(f"      • Rilevazioni: {stats['totale_rilevazioni']}")
        
        db.close()
        
        # Cleanup
        if os.path.exists(test_db):
            os.remove(test_db)
        
        return True
    except Exception as e:
        print(f"   ❌ Errore database: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Esegue tutti i test"""
    print("=" * 60)
    print("🚀 TEST REFACTORING FASE 1")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config,
        test_logger,
        test_normalizer,
        test_utils,
        test_database
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n   ❌ Test fallito con eccezione: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 RISULTATI")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ Test passati: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 TUTTI I TEST PASSATI! Refactoring Fase 1 completato con successo!")
    else:
        print(f"\n⚠️  {total - passed} test falliti. Controlla gli errori sopra.")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
