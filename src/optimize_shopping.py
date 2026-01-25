"""
Script per ottimizzare la spesa da lista in file di testo
"""
import sys
from shopping_optimizer import ShoppingOptimizer
from logger import get_logger

logger = get_logger(__name__)


def load_shopping_list(filename: str) -> list:
    """
    Carica lista della spesa da file di testo
    
    Args:
        filename: Path del file (es. 'lista_spesa.txt')
    
    Returns:
        Lista di prodotti (una riga = un prodotto)
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Leggi righe, rimuovi spazi e righe vuote
            items = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        logger.info(f"Caricati {len(items)} prodotti da {filename}")
        return items
    except FileNotFoundError:
        logger.error(f"File non trovato: {filename}")
        print(f"❌ File '{filename}' non trovato!")
        print(f"\nCrea un file con questo formato:")
        print("latte")
        print("pane")
        print("pasta")
        print("olio")
        return []
    except Exception as e:
        logger.error(f"Errore lettura file: {e}")
        return []


def main():
    """Entry point"""
    # Nome file di default
    filename = "lista_spesa.txt"
    
    # Permetti di specificare un file diverso
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    print(f"📋 Carico lista della spesa da: {filename}")
    
    # Carica lista
    shopping_list = load_shopping_list(filename)
    
    if not shopping_list:
        print("\n💡 Uso: python optimize_shopping.py [lista_spesa.txt]")
        return
    
    print(f"✅ {len(shopping_list)} prodotti caricati\n")
    
    # Ottimizza
    optimizer = ShoppingOptimizer()
    results = optimizer.find_best_supermarkets(shopping_list, top_n=3)
    
    # Stampa risultati
    optimizer.print_results(results, shopping_list)
    
    optimizer.close()


if __name__ == "__main__":
    main()
