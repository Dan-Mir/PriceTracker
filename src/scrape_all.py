"""
Script principale per lo scraping di tutti i supermercati
"""
import argparse
from src.logger import get_logger

logger = get_logger(__name__)


def scrape_eurospin():
    """Scraping Eurospin"""
    from eurospin.parser import EurospinParser
    import os
    from dotenv import load_dotenv
    
    load_dotenv("../.env")
    email = os.getenv("EUROSPIN_EMAIL")
    
    if not email:
        logger.error("EUROSPIN_EMAIL non trovato in .env")
        return 0
    
    logger.info("=" * 60)
    logger.info("SCRAPING EUROSPIN")
    logger.info("=" * 60)
    
    parser = EurospinParser()
    try:
        parser.login_interattivo(email)
        total = parser.get_total_products_saved()
        logger.info(f"✅ Eurospin completato: {total} prodotti totali")
        return total
    except Exception as e:
        logger.error(f"❌ Errore Eurospin: {e}", exc_info=True)
        return 0
    finally:
        parser.close()


def scrape_castoro():
    """Scraping Castoro"""
    from castoro.castoro_parser import CastoroParser
    
    logger.info("=" * 60)
    logger.info("SCRAPING CASTORO SHOP")
    logger.info("=" * 60)
    
    parser = CastoroParser()
    try:
        total = parser.scrape_all()
        logger.info(f"✅ Castoro completato: {total} prodotti")
        return total
    except Exception as e:
        logger.error(f"❌ Errore Castoro: {e}", exc_info=True)
        return 0
    finally:
        parser.close()


def scrape_all():
    """Scraping di tutti i supermercati"""
    logger.info("🛒 SCRAPING TUTTI I SUPERMERCATI")
    logger.info("=" * 60)
    
    totals = {}
    
    # Eurospin
    try:
        totals['Eurospin'] = scrape_eurospin()
    except Exception as e:
        logger.error(f"Errore Eurospin: {e}")
        totals['Eurospin'] = 0
    
    # Castoro
    try:
        totals['Castoro'] = scrape_castoro()
    except Exception as e:
        logger.error(f"Errore Castoro: {e}")
        totals['Castoro'] = 0
    
    # Riepilogo
    logger.info("=" * 60)
    logger.info("📊 RIEPILOGO SCRAPING")
    logger.info("=" * 60)
    
    total_global = 0
    for supermarket, count in totals.items():
        logger.info(f"  {supermarket}: {count} prodotti")
        total_global += count
    
    logger.info("=" * 60)
    logger.info(f"✅ TOTALE: {total_global} prodotti da {len(totals)} supermercati")
    
    return total_global


def main():
    """Main con argparse"""
    parser = argparse.ArgumentParser(
        description="Scraping prezzi supermercati italiani"
    )
    
    parser.add_argument(
        '--supermarket',
        choices=['eurospin', 'castoro', 'all'],
        default='all',
        help='Supermercato da scrapare (default: all)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.supermarket == 'eurospin':
            scrape_eurospin()
        elif args.supermarket == 'castoro':
            scrape_castoro()
        else:
            scrape_all()
    
    except KeyboardInterrupt:
        logger.info("\n⚠️  Scraping interrotto dall'utente")
    except Exception as e:
        logger.error(f"❌ Errore fatale: {e}", exc_info=True)


if __name__ == "__main__":
    main()
