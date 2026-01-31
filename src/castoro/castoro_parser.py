"""
Parser completo per Castoro Shop (https://www.castoro.shop)
SPA Vue.js - richiede Selenium per il rendering dinamico
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import platform
from typing import List, Dict, Optional

try:
    from ..db import PriceDatabase
    from ..logger import get_logger
    from ..normalizer import ProductNormalizer
    from .castoro_all_urls import CASTORO_SUBCATEGORY_URLS
    from .. import config
except ImportError:
    from src.db import PriceDatabase
    from src.logger import get_logger
    from src.normalizer import ProductNormalizer
    from src.castoro.castoro_all_urls import CASTORO_SUBCATEGORY_URLS
    from src import config

logger = get_logger(__name__)


class CastoroParser:
    """Parser per il sito Castoro Shop"""
    
    BASE_URL = "https://www.castoro.shop"
    SUPERMARKET_NAME = "Castoro"
    
    # Sottocategorie estratte automaticamente da castoro_categories.txt (109 totali)
    # Include TUTTE le categorie del sito per massima copertura prodotti
    # Script generazione: generate_castoro_urls.py
    SUBCATEGORIES = CASTORO_SUBCATEGORY_URLS

    
    def __init__(self, headless: bool = True):
        """
        Inizializza il parser
        
        Args:
            headless: Se True, esegue il browser in modalità headless
        """
        logger.info("Inizializzazione CastoroParser")
        
        self.headless = headless
        self.db = PriceDatabase()
        self.normalizer = ProductNormalizer()
        self.driver = None
        self.wait = None
        
        logger.info(f"CastoroParser inizializzato (headless={headless})")
    
    def _setup_driver(self):
        """Configura il driver Selenium per Chromium"""
        logger.info("Configurazione driver Chromium...")
        
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless=new')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36')
        
        # Detect ARM architecture
        if platform.machine() in ['aarch64', 'armv7l', 'arm64']:
            logger.info("ARM architecture detectata, uso Chromium")
            options.binary_location = '/usr/bin/chromium'
            from selenium.webdriver.chrome.service import Service
            service = Service(executable_path='/usr/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            self.driver = webdriver.Chrome(options=options)
        
        self.wait = WebDriverWait(self.driver, config.SELENIUM_TIMEOUT)
        logger.info("Driver configurato con successo")
    
    def scrape_all(self) -> int:
        """
        Esegue lo scraping completo del sito
        
        Returns:
            Numero totale di prodotti scrapati
        """
        logger.info("=" * 60)
        logger.info(f"INIZIO SCRAPING {self.SUPERMARKET_NAME}")
        logger.info("=" * 60)
        
        total_products = 0
        
        try:
            self._setup_driver()
            
            # Carica homepage
            logger.info(f"Caricamento {self.BASE_URL}")
            self.driver.get(self.BASE_URL)
            time.sleep(config.PAGE_LOAD_DELAY)
            
            # Rimuovi cookie banner
            self._remove_cookie_banner()
            
            # Scraping per ogni sottocategoria
            for i, subcategory_url in enumerate(self.SUBCATEGORIES, 1):
                # Estrai nome categoria dall'URL
                category_name = subcategory_url.split('/')[-1].replace('-', ' ').title()
                logger.info(f"\n[{i}/{len(self.SUBCATEGORIES)}] Scraping: {category_name}")
                
                products = self._scrape_category_by_url(subcategory_url)
                
                if products:
                    self._save_products(products)
                    total_products += len(products)
                    logger.info(f"✅ {category_name}: {len(products)} prodotti salvati")
                else:
                    logger.warning(f"⚠️  {category_name}: nessun prodotto trovato")
                
                # Delay tra categorie
                time.sleep(config.CATEGORY_DELAY)
            
            # Aggiorna timestamp
            self.db.update_supermercato_scraping(self.SUPERMARKET_NAME)
            
            logger.info("=" * 60)
            logger.info(f"✅ SCRAPING COMPLETATO: {total_products} prodotti totali")
            logger.info("=" * 60)
            
            return total_products
            
        except KeyboardInterrupt:
            logger.warning("Scraping interrotto dall'utente")
            raise
        except Exception as e:
            logger.error(f"Errore durante scraping: {e}", exc_info=True)
            raise
        finally:
            self.close()
    
    
    def _remove_cookie_banner(self):
        """Rimuove il banner dei cookie con JavaScript"""
        try:
            logger.debug("Rimozione cookie banner...")
            self.driver.execute_script("""
                var banner = document.getElementById('iubenda-cs-banner');
                if (banner) {
                    banner.remove();
                }
            """)
            time.sleep(1)
            logger.debug("Cookie banner rimosso")
        except Exception as e:
            logger.debug(f"Nessun cookie banner da rimuovere: {e}")
    
    def _scrape_category_by_url(self, category_url: str) -> List[Dict]:
        """
        Scraping di una singola categoria usando l'URL diretto
        Gestisce automaticamente la paginazione
        
        Args:
            category_url: URL della categoria (es: /category/frutta-e-verdura/frutta-fresca)
        
        Returns:
            Lista di prodotti estratti
        """
        all_products = []
        page = 1
        max_pages = 20  # Limite di sicurezza
        
        try:
            category_name = category_url.split('/')[-1].replace('-', ' ').title()
            
            while page <= max_pages:
                # Costruisci URL con paginazione
                full_url = f"{self.BASE_URL}{category_url}?page={page}"
                
                logger.info(f"Navigazione a: {full_url} (pagina {page})")
                self.driver.get(full_url)
                time.sleep(config.PAGE_LOAD_DELAY)
                
                # Scroll per caricare prodotti lazy-loaded
                self._scroll_to_load()
                
                # Estrai prodotti dalla pagina corrente
                product_cards = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    ".product.product-card"
                )
                
                # Se non ci sono prodotti, abbiamo finito
                if not product_cards:
                    logger.info(f"Nessun prodotto trovato a pagina {page}, fine paginazione")
                    break
                
                logger.info(f"Trovati {len(product_cards)} prodotti a pagina {page}")
                
                page_products = 0
                for card in product_cards:
                    try:
                        product = self._extract_product_from_card(card, category_name)
                        if product:
                            all_products.append(product)
                            page_products += 1
                    except Exception as e:
                        logger.debug(f"Errore estrazione prodotto: {e}")
                        continue
                
                # Se non abbiamo estratto prodotti validi, potremmo essere alla fine
                if page_products == 0:
                    logger.info(f"Nessun prodotto valido a pagina {page}, fine paginazione")
                    break
                
                # Verifica se esiste pulsante "next" o se siamo all'ultima pagina
                try:
                    # Cerca pulsante next disabilitato (indica ultima pagina)
                    next_button = self.driver.find_element(
                        By.CSS_SELECTOR,
                        ".swiper-button-next.swiper-button-disabled"
                    )
                    logger.info(f"Ultima pagina raggiunta (pagina {page})")
                    break
                except:
                    # Pulsante next non disabilitato, continua
                    pass
                
                page += 1
                time.sleep(2)  # Delay tra pagine
        
        except Exception as e:
            logger.error(f"Errore scraping categoria {category_url}: {e}", exc_info=True)
        
        logger.info(f"Totale prodotti estratti da {category_name}: {len(all_products)} ({page} pagine)")
        return all_products
    
    def _scrape_category(self, category_name: str) -> List[Dict]:
        """
        Scraping di una singola categoria
        
        Args:
            category_name: Nome della categoria
        
        Returns:
            Lista di prodotti estratti
        """
        products = []
        
        try:
            # Genera URL categoria
            slug = self._generate_slug(category_name)
            category_url = f"{self.BASE_URL}/category/{slug}"
            
            logger.info(f"Navigazione a: {category_url}")
            self.driver.get(category_url)
            time.sleep(config.PAGE_LOAD_DELAY)
            
            # Scroll per caricare prodotti lazy-loaded
            self._scroll_to_load()
            
            # Estrai prodotti
            product_cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".product.product-card"
            )
            
            logger.info(f"Trovati {len(product_cards)} prodotti")
            
            for card in product_cards:
                try:
                    product = self._extract_product_from_card(card, category_name)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Errore estrazione prodotto: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Errore scraping categoria {category_name}: {e}", exc_info=True)
        
        return products
    
    def _generate_slug(self, text: str) -> str:
        """Genera slug URL da testo"""
        slug = text.lower()
        
        # NON rimuovere ' e ', mantienilo ma con trattino
        slug = slug.replace(' e ', '-e-')
        slug = slug.replace(', ', '-')
        slug = slug.replace(' ', '-')
        
        # Rimuovi accenti
        accents = {
            'à': 'a', 'è': 'e', 'é': 'e', 'ì': 'i',
            'ò': 'o', 'ù': 'u', 'À': 'a', 'È': 'e',
            'É': 'e', 'Ì': 'i', 'Ò': 'o', 'Ù': 'u'
        }
        for old, new in accents.items():
            slug = slug.replace(old, new)
        
        return slug
    
    def _scroll_to_load(self):
        """Scrolla la pagina per caricare prodotti lazy-loaded"""
        logger.debug("Scroll per lazy loading...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        attempts = 0
        max_attempts = 5
        
        while attempts < max_attempts:
            # Scrolla giù
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(config.SCROLL_DELAY)
            
            # Calcola nuova altezza
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height
            attempts += 1
        
        logger.debug(f"Scroll completato ({attempts} tentativi)")
    
    def _extract_product_from_card(self, card_element, category: str) -> Optional[Dict]:
        """
        Estrae i dati prodotto da una card
        
        Args:
            card_element: Elemento Selenium della card prodotto
            category: Nome categoria
        
        Returns:
            Dict con dati prodotto o None
        """
        try:
            # Nome prodotto
            try:
                name_elem = card_element.find_element(By.CSS_SELECTOR, ".product-name")
                nome = name_elem.text.strip()
            except NoSuchElementException:
                logger.debug("Nome prodotto non trovato")
                return None
            
            if not nome:
                return None
            
            # Prezzo
            try:
                price_elem = card_element.find_element(By.CSS_SELECTOR, ".product-price")
                prezzo_text = price_elem.text.strip()
                prezzo = self._parse_price(prezzo_text)
            except NoSuchElementException:
                logger.debug(f"Prezzo non trovato per {nome}")
                return None
            
            if prezzo is None or prezzo <= 0:
                return None
            
            # Marca (opzionale)
            marca = None
            try:
                brand_elem = card_element.find_element(By.CSS_SELECTOR, ".product-brand")
                marca = brand_elem.text.strip()
            except NoSuchElementException:
                # Prova ad estrarre dal nome
                marca = self.normalizer.extract_brand_from_text(nome)
            
            # Descrizione (per unità di misura)
            unita_misura = None
            try:
                descr_elem = card_element.find_element(By.CSS_SELECTOR, ".product-descr")
                descr_text = descr_elem.text.strip()
                unita_misura = self.normalizer.extract_unit(descr_text)
            except NoSuchElementException:
                # Prova ad estrarre dal nome
                unita_misura = self.normalizer.extract_unit(nome)
            
            # Verifica se in offerta
            in_offerta = False
            sconto_percentuale = None
            prezzo_listino = prezzo
            
            try:
                # Cerca elementi promo
                promo_elem = card_element.find_element(
                    By.CSS_SELECTOR,
                    ".product-description.has-promo, .promo_discount"
                )
                
                if promo_elem:
                    in_offerta = True
                    
                    # Cerca prezzo originale se presente
                    try:
                        old_price_elem = card_element.find_element(
                            By.CSS_SELECTOR,
                            ".old-price, .price-before"
                        )
                        old_price = self._parse_price(old_price_elem.text)
                        
                        if old_price and old_price > prezzo:
                            prezzo_listino = old_price
                            sconto_percentuale = round(((old_price - prezzo) / old_price) * 100, 2)
                    except NoSuchElementException:
                        pass
            
            except NoSuchElementException:
                pass
            
            product = {
                'nome': nome,
                'marca': marca,
                'categoria': category,
                'unita_misura': unita_misura,
                'prezzo_attuale': prezzo,
                'prezzo_listino': prezzo_listino,
                'in_offerta': in_offerta,
                'sconto_percentuale': sconto_percentuale
            }
            
            logger.debug(f"Estratto: {nome} - €{prezzo:.2f}")
            return product
            
        except Exception as e:
            logger.debug(f"Errore estrazione prodotto: {e}")
            return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Converte testo prezzo in float
        
        Args:
            price_text: Testo contenente il prezzo
        
        Returns:
            Prezzo come float o None
        """
        try:
            # Rimuovi simboli e spazi
            price_clean = price_text.replace('€', '').replace(',', '.').strip()
            
            # Estrai numero con regex
            match = re.search(r'(\d+\.?\d*)', price_clean)
            if match:
                return float(match.group(1))
            
            return None
        except Exception as e:
            logger.debug(f"Errore parsing prezzo '{price_text}': {e}")
            return None
    
    def _save_products(self, products: List[Dict]):
        """
        Salva prodotti nel database
        
        Args:
            products: Lista di prodotti da salvare
        """
        saved = 0
        
        for product in products:
            try:
                # Normalizza nome
                nome_normalizzato = self.normalizer.normalize_text(product['nome'])
                
                # Salva nel DB (in_offerta e sconto_percentuale sono calcolati automaticamente)
                self.db.upsert_product(
                    nome=nome_normalizzato,
                    marca=product.get('marca'),
                    categoria=product.get('categoria'),
                    unita_misura=product.get('unita_misura'),
                    prezzo_attuale=product['prezzo_attuale'],
                    prezzo_listino=product.get('prezzo_listino', product['prezzo_attuale']),
                    supermercato=self.SUPERMARKET_NAME
                )
                saved += 1
            except Exception as e:
                logger.error(f"Errore salvataggio prodotto {product.get('nome')}: {e}")
                continue
        
        logger.debug(f"Salvati {saved}/{len(products)} prodotti")
    
    def close(self):
        """Chiude il browser e il database"""
        if self.driver:
            try:
                self.driver.quit()
                logger.debug("Browser chiuso")
            except:
                pass
        
        if self.db:
            try:
                self.db.close()
                logger.debug("Database chiuso")
            except:
                pass


def main():
    """Test standalone del parser"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scraping Castoro Shop")
    parser.add_argument('--no-headless', action='store_true', help='Mostra il browser')
    args = parser.parse_args()
    
    castoro = CastoroParser(headless=not args.no_headless)
    
    try:
        total = castoro.scrape_all()
        print(f"\n✅ Scraping completato: {total} prodotti salvati")
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrotto dall'utente")
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
    finally:
        castoro.close()


if __name__ == "__main__":
    main()
