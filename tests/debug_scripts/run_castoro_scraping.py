#!/usr/bin/env python3
"""
Script per eseguire lo scraping completo di Castoro Shop
Mostra log e progressi in tempo reale

Utilizzo:
    python run_castoro_scraping.py
"""

import sys
import time
from datetime import datetime

# Aggiungi src al path
sys.path.insert(0, 'src')

from src.castoro.castoro_parser import CastoroParser
from db import PriceDatabase

def print_header():
    """Stampa header iniziale"""
    print("\n" + "="*70)
    print("🛒  SCRAPING CASTORO SHOP - Tutte le categorie con paginazione")
    print("="*70)
    print(f"📅 Avviato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Sottocategorie da scrapare: 109")
    print(f"🔄 Con gestione paginazione automatica")
    print("="*70 + "\n")

def print_stats(start_time, total_products):
    """Stampa statistiche finali"""
    duration = time.time() - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    
    print("\n" + "="*70)
    print("✅  SCRAPING COMPLETATO!")
    print("="*70)
    print(f"📦 Prodotti totali: {total_products}")
    print(f"⏱️  Tempo impiegato: {minutes}m {seconds}s")
    print(f"📅 Completato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Mostra statistiche database
    try:
        db = PriceDatabase()
        stats = db.get_stats()
        print(f"\n📊 Database aggiornato:")
        print(f"   • Prodotti totali: {stats['totale_prodotti']}")
        print(f"   • Supermercati: {stats['totale_supermercati']}")
        print(f"   • Rilevazioni: {stats['totale_rilevazioni']}")
    except Exception as e:
        print(f"⚠️  Errore lettura stats: {e}")
    
    print("="*70 + "\n")

def main():
    """Funzione principale"""
    print_header()
    
    start_time = time.time()
    total_products = 0
    
    try:
        # Inizializza parser
        print("🔧 Inizializzazione parser Selenium...\n")
        parser = CastoroParser(headless=True)
        
        # Esegui scraping
        print("🚀 Inizio scraping...\n")
        total_products = parser.scrape_all()
        
        # Statistiche finali
        print_stats(start_time, total_products)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrotto dall'utente")
        duration = time.time() - start_time
        print(f"⏱️  Tempo parziale: {int(duration//60)}m {int(duration%60)}s")
        print(f"📦 Prodotti salvati finora: {total_products}\n")
        return 1
        
    except Exception as e:
        print(f"\n\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
