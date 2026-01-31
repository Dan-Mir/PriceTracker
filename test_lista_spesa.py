#!/usr/bin/env python3
"""
Test LLM ibrido con lista della spesa
FunctionGemma (locale) + Gemini API (cloud)
"""
from src.gemini_optimizer import HybridShoppingOptimizer
import sys

def main():
    """Test con lista della spesa"""
    print("=" * 80)
    print("🛒 TEST IBRIDO: FUNCTIONGEMMA + GEMINI API".center(80))
    print("=" * 80)
    print()
    
    # Leggi lista spesa
    try:
        with open('lista_spesa.txt', 'r', encoding='utf-8') as f:
            prodotti = [p.strip() for p in f.readlines() if p.strip()]
    except FileNotFoundError:
        print("❌ File lista_spesa.txt non trovato!")
        return
    
    print("📋 LISTA DELLA SPESA:")
    for i, prodotto in enumerate(prodotti, 1):
        print(f"   {i}. {prodotto}")
    print()
    
    # Inizializza ottimizzatore ibrido
    print("🤖 Inizializzo ottimizzatore ibrido...")
    print("   • FunctionGemma (locale) per estrazione keywords")
    print("   • Gemini API (cloud) per ragionamento semantico")
    print()
    
    try:
        optimizer = HybridShoppingOptimizer()
        print("✅ Ottimizzatore pronto!\n")
    except Exception as e:
        print(f"❌ Errore inizializzazione: {e}")
        print("💡 Verifica:")
        print("   - Ollama in esecuzione: ollama serve")
        print("   - GEMINI_API_KEY nel file .env")
        return
    
    print("=" * 80)
    print()
    print("🔄 STEP 1: FunctionGemma estrae keywords...")
    print("🔄 STEP 2: Query database per ogni prodotto...")
    print("🔄 STEP 3: Gemini API seleziona i match migliori...")
    print()
    
    try:
        result = optimizer.optimize_shopping_list(prodotti)
        output = optimizer.format_result(result)
        print(output)
    except Exception as e:
        print(f"❌ Errore durante l'ottimizzazione: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("✅ Test completato!")
    print()


if __name__ == "__main__":
    main()
