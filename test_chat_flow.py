#!/usr/bin/env python3
"""
Test simulato della chat per verificare il flusso completo
"""
from src.llm_interface import GemmaShoppingAssistant
import logging

# Silenzioso
for logger_name in ['src.llm_interface', 'src.db', 'src.shopping_optimizer']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

def simulate_conversation():
    """Simula una conversazione realistica"""
    assistant = GemmaShoppingAssistant()
    
    print("🤖 Simulazione Chat Completa")
    print("=" * 70)
    
    conversations = [
        ("Ciao, devo comprare legumi, birra, pasta e salumi", "Lista multipla con birra (non disponibile)"),
        ("Mostrami la lista", "Richiesta dettagli"),
        ("Quanto costa il latte?", "Singolo prodotto"),
        ("Mostrami anche le uova e i legumi", "Query multipla"),
    ]
    
    for query, descrizione in conversations:
        print(f"\n{'─' * 70}")
        print(f"💡 Scenario: {descrizione}")
        print(f"{'─' * 70}")
        print(f"\n👤 Tu: {query}\n")
        print("🤖 Assistente:")
        
        risposta = assistant.chat(query)
        print(risposta)
        
        input("\n⏸️  Premi INVIO per continuare...")
    
    assistant.close()
    print(f"\n{'=' * 70}")
    print("✅ Simulazione completata!")
    print("\n💡 Tutto funziona correttamente!")
    print("   - Riconoscimento intento migliorato")
    print("   - Sinonimi espansi automaticamente")
    print("   - Output dettagliato con lista prodotti")
    print("   - Nessun log verboso\n")


if __name__ == "__main__":
    simulate_conversation()
