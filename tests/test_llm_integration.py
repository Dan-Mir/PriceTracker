"""
Test per l'integrazione LLM
"""
import sys
import os

# Aggiungi il path del progetto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.db import PriceDatabase
from src.shopping_optimizer import ShoppingOptimizer


def test_shopping_optimizer_basic():
    """Test base dello shopping optimizer senza LLM"""
    print("\n" + "="*60)
    print("TEST: Shopping Optimizer (senza LLM)")
    print("="*60)
    
    db = PriceDatabase()
    optimizer = ShoppingOptimizer(db)
    
    # Lista spesa di test
    lista_spesa = ["latte", "pane", "pasta", "olio"]
    
    print(f"\n📝 Lista spesa: {lista_spesa}")
    
    results = optimizer.find_best_supermarkets(lista_spesa, top_n=3)
    
    if not results:
        print("❌ Nessun risultato trovato (database potrebbe essere vuoto)")
        print("   Esegui prima: python src/main.py")
        return False
    
    print(f"\n✅ Trovati {len(results)} supermercati")
    
    optimizer.print_results(results, lista_spesa)
    
    optimizer.close()
    return True


def test_db_methods():
    """Test dei nuovi metodi del database"""
    print("\n" + "="*60)
    print("TEST: Metodi Database")
    print("="*60)
    
    db = PriceDatabase()
    
    # Test 1: search_products
    print("\n1️⃣  Test search_products('latte'):")
    results = db.search_products("latte", limit=3)
    if results:
        for r in results:
            print(f"   - {r['nome']} ({r['marca']}) → €{r['prezzo']:.2f} @ {r['supermercato']}")
        print("   ✅ OK")
    else:
        print("   ⚠️  Nessun risultato (database vuoto?)")
    
    # Test 2: get_products_in_offer
    print("\n2️⃣  Test get_products_in_offer(min_sconto=5):")
    offerte = db.get_products_in_offer(min_sconto=5.0, limit=3)
    if offerte:
        for o in offerte:
            print(f"   - {o[0]} ({o[1]}) → {o[2]:.2f}€ → {o[3]:.2f}€ (-{o[4]:.0f}%)")
        print("   ✅ OK")
    else:
        print("   ⚠️  Nessuna offerta trovata")
    
    # Test 3: get_price_history
    print("\n3️⃣  Test get_price_history('latte'):")
    storico = db.get_price_history("latte", limit=3)
    if storico:
        for h in storico:
            print(f"   - {h[1]}: €{h[0]:.2f} @ {h[2]}")
        print("   ✅ OK")
    else:
        print("   ⚠️  Nessuno storico trovato")
    
    # Test 4: get_all_supermarkets
    print("\n4️⃣  Test get_all_supermarkets():")
    supermercati = db.get_all_supermarkets()
    if supermercati:
        print(f"   Supermercati: {', '.join(supermercati)}")
        print("   ✅ OK")
    else:
        print("   ⚠️  Nessun supermercato trovato")
    
    db.close()
    return True


def test_llm_available():
    """Verifica se Ollama è disponibile"""
    print("\n" + "="*60)
    print("TEST: Disponibilità LLM")
    print("="*60)
    
    try:
        import ollama
        print("✅ Ollama package installato")
        
        # Test connessione
        try:
            models = ollama.list()
            print(f"✅ Server Ollama raggiungibile")
            
            if models.get('models'):
                print(f"\n📦 Modelli disponibili:")
                for model in models['models']:
                    print(f"   - {model['name']}")
                
                # Check se gemma2:2b o tinyllama sono disponibili
                model_names = [m['name'] for m in models['models']]
                if any('gemma2' in name for name in model_names):
                    print("\n✅ gemma2 trovato - pronto per l'uso!")
                elif any('tinyllama' in name for name in model_names):
                    print("\n✅ tinyllama trovato - pronto per l'uso!")
                else:
                    print("\n⚠️  Nessun modello compatibile trovato")
                    print("   Scarica un modello con: ollama pull gemma2:2b")
            else:
                print("⚠️  Nessun modello scaricato")
                print("   Scarica un modello con: ollama pull gemma2:2b")
        
        except Exception as e:
            print(f"❌ Server Ollama non raggiungibile: {e}")
            print("   Avvia il server con: ollama serve")
            return False
        
        return True
    
    except ImportError:
        print("❌ Ollama package non installato")
        print("   Installa con: pip install ollama")
        return False


def test_llm_integration():
    """Test completo integrazione LLM"""
    print("\n" + "="*60)
    print("TEST: Integrazione LLM")
    print("="*60)
    
    try:
        from src.llm_interface import GemmaShoppingAssistant
        
        print("\n🤖 Inizializzo assistente LLM...")
        assistant = GemmaShoppingAssistant()
        
        # Test 1: Query semplice
        print("\n1️⃣  Test query: 'Dove trovo il latte?'")
        risposta = assistant.chat("Dove trovo il latte?")
        print(f"   Risposta: {risposta[:200]}...")
        print("   ✅ OK")
        
        # Test 2: Ottimizzazione
        print("\n2️⃣  Test ottimizzazione: 'Cerca latte, pane e pasta'")
        risposta = assistant.chat("Voglio comprare latte, pane e pasta")
        print(f"   Risposta: {risposta[:200]}...")
        print("   ✅ OK")
        
        assistant.close()
        return True
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False


def main():
    """Esegue tutti i test"""
    print("\n" + "🧪 TEST SUITE FASE 2 - LLM INTEGRATION".center(60, "="))
    
    tests = [
        ("Database Methods", test_db_methods),
        ("Shopping Optimizer", test_shopping_optimizer_basic),
        ("LLM Availability", test_llm_available),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ ERRORE in {test_name}: {e}")
            results[test_name] = False
    
    # Test LLM integration solo se Ollama è disponibile
    if results.get("LLM Availability", False):
        print("\n" + "="*60)
        print("Ollama disponibile - Test integrazione LLM...")
        print("="*60)
        try:
            results["LLM Integration"] = test_llm_integration()
        except Exception as e:
            print(f"\n❌ ERRORE LLM Integration: {e}")
            results["LLM Integration"] = False
    else:
        print("\n" + "="*60)
        print("⏭️  Saltato test LLM Integration (Ollama non disponibile)")
        print("="*60)
    
    # Riepilogo
    print("\n" + "="*60)
    print("RIEPILOGO TEST")
    print("="*60)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n📊 Risultato: {passed}/{total} test passati")
    
    if passed == total:
        print("\n🎉 TUTTI I TEST PASSATI!")
    elif passed > 0:
        print("\n⚠️  ALCUNI TEST FALLITI")
    else:
        print("\n❌ TUTTI I TEST FALLITI")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
