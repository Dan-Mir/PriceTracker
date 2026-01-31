"""
Script per visualizzare i prodotti in offerta dal database
"""
from src.db import PriceDatabase
from src.logger import get_logger

logger = get_logger(__name__)

def mostra_offerte():
    db = PriceDatabase()
    
    print("\n🎯 === PRODOTTI IN OFFERTA === 🎯\n")
    
    # Statistiche generali
    stats = db.get_stats()
    print(f"📊 Statistiche Database:")
    print(f"   • Prodotti totali: {stats['totale_prodotti']}")
    print(f"   • Supermercati: {stats['totale_supermercati']}")
    print(f"   • Rilevazioni prezzi: {stats['totale_rilevazioni']}")
    print(f"   • Prodotti in offerta: {stats['prodotti_in_offerta']}")
    
    # Mostra le offerte (minimo 5% di sconto)
    offerte = db.get_products_in_offer(min_sconto=5)
    
    if not offerte:
        print("\n❌ Nessuna offerta trovata al momento.")
        db.close()
        return
    
    print(f"\n🔥 Top {len(offerte)} Offerte (sconto >= 5%):\n")
    print(f"{'PRODOTTO':<40} {'MARCA':<15} {'PRIMA':<10} {'ORA':<10} {'SCONTO':<10} {'SUPERMERCATO':<15}")
    print("=" * 110)
    
    for offerta in offerte:
        nome, marca, prezzo_listino, prezzo_attuale, sconto_pct, supermercato, data = offerta
        
        marca_str = marca if marca else "-"
        print(f"{nome[:39]:<40} {marca_str[:14]:<15} €{prezzo_listino:>7.2f} €{prezzo_attuale:>7.2f} {sconto_pct:>7.1f}% {supermercato:<15}")
    
    db.close()

if __name__ == "__main__":
    mostra_offerte()
