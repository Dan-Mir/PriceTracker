#!/usr/bin/env python3
"""
Demo rapida dell'Assistente Spesa con LLM
"""
from src.llm_interface import GemmaShoppingAssistant

def main():
    """Demo con query predefinite"""
    print("=" * 70)
    print("🤖 ASSISTENTE SPESA - DEMO".center(70))
    print("=" * 70)
    print()
    
    assistant = GemmaShoppingAssistant()
    print(f"✅ Modello: {assistant.model}\n")
    
    # Demo queries
    queries = [
        "Dove trovo il latte più economico?",
        "Voglio comprare latte, pane e pasta",
        "Quanto costa l'olio?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'━' * 70}")
        print(f"📝 Query {i}: {query}")
        print('━' * 70)
        
        risposta = assistant.chat(query)
        print(risposta)
    
    assistant.close()
    
    print(f"\n{'=' * 70}")
    print("\n💡 Per la chat interattiva, usa: python src/llm_interface.py")
    print("💡 Per ottimizzare una lista: python src/optimize_shopping.py")
    print()


if __name__ == "__main__":
    main()
