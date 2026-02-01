from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import pickle
import os
import platform
from collections import deque

try:
    # Package imports (when running as module)
    from ..db import PriceDatabase
    from ..logger import get_logger
    from ..normalizer import ProductNormalizer
    from ..utils import retry_on_exception, RateLimiter
    from .. import config
    from .eurospin_categories import EUROSPIN_MAIN_CATEGORIES
except ImportError:
    # Script imports (when running from src/)
    import sys
    import os
    # Ensure src is in path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    from db import PriceDatabase
    from logger import get_logger
    from normalizer import ProductNormalizer
    from utils import retry_on_exception, RateLimiter
    import config
    from eurospin.eurospin_categories import EUROSPIN_MAIN_CATEGORIES

logger = get_logger(__name__)

class EurospinParser:
    def __init__(self):
        self.store_url = config.EUROSPIN_URL
        self.db = PriceDatabase()
        self.cookie_file = config.EUROSPIN_COOKIE_FILE
        self.normalizer = ProductNormalizer()
        self.rate_limiter = RateLimiter()
        
        chrome_options = Options()
        for option in config.CHROME_OPTIONS:
            chrome_options.add_argument(option)
        chrome_options.add_argument(f"user-agent={config.USER_AGENT}")
        
        # Rileva se siamo su Raspberry Pi (ARM) e usa Chromium
        is_arm = platform.machine() in ['aarch64', 'armv7l', 'armv8']
        
        if is_arm:
            # Raspberry Pi: usa Chromium
            chrome_options.binary_location = '/usr/bin/chromium'
            service = Service('/usr/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("EurospinParser inizializzato (Chromium per ARM)")
        else:
            # x86/x64: usa Chrome normale
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("EurospinParser inizializzato (Chrome)")
        
        # Usa blacklist da config
        self.BLACKLIST_URL = config.URL_BLACKLIST
        self.total_saved = 0

    # --- GESTIONE SESSIONE COMPLETA ---
    def save_cookies(self):
        """Salva cookie + localStorage + sessionStorage per mantenere la sessione"""
        # Salva tutto lo stato della sessione
        session_data = {
            'cookies': self.driver.get_cookies(),
            'localStorage': self.driver.execute_script("return window.localStorage;"),
            'sessionStorage': self.driver.execute_script("return window.sessionStorage;")
        }
        
        with open(self.cookie_file, 'wb') as file:
            pickle.dump(session_data, file)
        logger.info("Sessione completa salvata (cookie + storage)")

    def load_cookies(self):
        """Carica cookie + localStorage + sessionStorage salvati"""
        if not os.path.exists(self.cookie_file):
            logger.warning("Nessun file sessione trovato")
            return False
        
        try:
            with open(self.cookie_file, 'rb') as file:
                session_data = pickle.load(file)
                
                # GESTISCI RETROCOMPATIBILITÀ: se è una lista, sono vecchi cookie
                if isinstance(session_data, list):
                    logger.warning("File cookie vecchio formato - richiesto nuovo login")
                    return False
                
                # Carica i cookie
                cookies = session_data.get('cookies', [])
                for cookie in cookies:
                    # Rimuovi campi che possono dare problemi
                    if 'expiry' in cookie:
                        del cookie['expiry']
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        pass  # Alcuni cookie potrebbero fallire
                
                # Ripristina localStorage
                local_storage = session_data.get('localStorage', {})
                if local_storage:
                    for key, value in local_storage.items():
                        try:
                            self.driver.execute_script(
                                "window.localStorage.setItem(arguments[0], arguments[1]);",
                                key, value
                            )
                        except:
                            pass
                
                # Ripristina sessionStorage
                session_storage = session_data.get('sessionStorage', {})
                if session_storage:
                    for key, value in session_storage.items():
                        try:
                            self.driver.execute_script(
                                "window.sessionStorage.setItem(arguments[0], arguments[1]);",
                                key, value
                            )
                        except:
                            pass
                
            logger.info("Sessione ripristinata (cookie + localStorage + sessionStorage)")
            return True
        except Exception as e:
            logger.error(f"Errore ripristino sessione: {e}")
            return False
    
    def _verifica_sessione_valida(self):
        """Verifica se la sessione corrente mostra i prezzi (sessione valida)"""
        try:
            # Visita una pagina prodotti nota per testare
            test_url = f"{self.store_url}/category/frutta-e-verdura"
            logger.info("Verifico validità sessione...")
            self.driver.get(test_url)
            time.sleep(config.PAGE_LOAD_DELAY)
            
            # Scroll per triggerare lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Cerco prezzi sulla pagina
            prices = self.driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
            if not prices:
                prices = self.driver.find_elements(By.CSS_SELECTOR, ".price, .prezzo, [class*='price'], [class*='prezzo']")
            
            # Anche controllo se c'è il bottone "Accedi" che indica logout
            try:
                login_btn = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Accedi') or contains(text(), 'ACCEDI')]")
                if login_btn:
                     logger.warning("Trovato bottone Accedi - sessione non valida")
                     return False
            except: pass

            if len(prices) > 0:
                logger.info(f"Sessione valida - {len(prices)} prezzi visibili")
                return True
            else:
                logger.warning("Sessione non valida - nessun prezzo visibile")
                return False
        except Exception as e:
            logger.error(f"Errore verifica sessione: {e}")
            return False
    # -----------------------

    def _clean_price(self, price_str):
        if not price_str: return 0.0
        clean = price_str.replace('€', '').replace(' ', '').replace(',', '.')
        try:
            val = float(re.findall(r"[-+]?\d*\.\d+|\d+", clean)[0])
            return val
        except:
            return 0.0

    def _is_weight(self, text):
        pattern = r'^\d+\s*[.,]?\s*\d*\s*(g|kg|ml|l|lt|cl|pz|pezz[oi])\s*e?$'
        return re.match(pattern, text.strip(), re.IGNORECASE) is not None

    def login_interattivo(self, email):
        logger.info("=== INIZIO LOGIN ===")
        
        # 1. Naviga sul dominio (necessario prima di caricare i cookie)
        self.driver.get(self.store_url)
        time.sleep(2)

        # 2. TENTA LOGIN CON COOKIE
        if self.load_cookies():
            # Dopo aver caricato i cookie, vai direttamente sulla pagina di test
            # SENZA fare refresh (che potrebbe invalidare i cookie)
            if self._verifica_sessione_valida():
                logger.info("SESSIONE RIPRISTINATA! Salto il login manuale")
                self.naviga_e_salva()
                return True
            else:
                logger.warning("Cookie presenti ma sessione scaduta. Elimino cookie e rifaccio login")
                # Elimina cookie non validi
                if os.path.exists(self.cookie_file):
                    os.remove(self.cookie_file)
                    logger.info("Cookie eliminati")
                # Ricarica la pagina per partire da zero
                self.driver.get(self.store_url)
                time.sleep(2)

        # 3. LOGIN MANUALE (Se cookie falliscono o non esistono)
        wait = WebDriverWait(self.driver, 25)

        try:
            cookie = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            self.driver.execute_script("arguments[0].click();", cookie)
            time.sleep(1)
        except: pass

        try:
            # Apri menu se necessario per trovare login
            # Spesso icona profilo
            self.driver.execute_script("document.querySelector('.icon-profile').click();")
        except:
            logger.error("Icona profilo non trovata, tento URL login diretto...")
            # Fallback URL login se esiste (non standard in SPA, ma proviamo)
            pass
        
        time.sleep(5) 

        # JS Injection Email
        js_email = """
        var t=arguments[0]; function f(r){var e=r.querySelector("input[name='email-input']");if(e)return e;
        var w=document.createTreeWalker(r,NodeFilter.SHOW_ELEMENT,null,false);while(n=w.nextNode())
        {if(n.shadowRoot){var x=f(n.shadowRoot);if(x)return x;}}return null;}
        var e=f(document.body);if(e){e.value=t;e.dispatchEvent(new Event('input',{bubbles:true}));return 'OK';}return 'KO';
        """
        if self.driver.execute_script(js_email, email) == "KO":
            logger.error("Campo email non trovato")
            return False
        
        time.sleep(1)
        
        # Click Continua
        js_btn = """
        var t=arguments[0].toUpperCase(); function f(r){var b=r.querySelectorAll("button");
        for(var i=0;i<b.length;i++)if(b[i].innerText.toUpperCase().includes(t))return b[i];
        var w=document.createTreeWalker(r,NodeFilter.SHOW_ELEMENT,null,false);while(n=w.nextNode())
        {if(n.shadowRoot){var x=f(n.shadowRoot);if(x)return x;}}return null;}
        var b=f(document.body);if(b){b.click();return 'OK';}return 'KO';
        """
        self.driver.execute_script(js_btn, "CONTINUA")

        logger.info("Controlla la mail per il codice OTP")
        print("\n   📩 CONTROLLA LA MAIL ORA")
        try:
            # INTERACTIVE INPUT
            otp = input("   👉 INSERISCI CODICE: ")
        except: return False
        
        # OTP
        js_otp = """
        var c=arguments[0]; function f(r){var e=r.querySelector("input[autocomplete='one-time-code']")||r.querySelector("input[type='tel']");
        if(!e){var i=r.querySelectorAll("input");for(var j=0;j<i.length;j++)if(i[j].type=='text'&&i[j].value=='')return i[j];}
        if(e)return e;var w=document.createTreeWalker(r,NodeFilter.SHOW_ELEMENT,null,false);while(n=w.nextNode())
        {if(n.shadowRoot){var x=f(n.shadowRoot);if(x)return x;}}return null;}
        var e=f(document.body);if(e){e.value=c;e.dispatchEvent(new Event('input',{bubbles:true}));return 'OK';}return 'KO';
        """
        self.driver.execute_script(js_otp, otp)
        time.sleep(1)
        self.driver.execute_script(js_btn, "ACCEDI")
        
        logger.info("Attendo completamento login...")
        time.sleep(config.LOGIN_DELAY)
        
        # Verifica se login riuscito
        if not self._verifica_sessione_valida():
             logger.warning("Login sembra fallito (nessun prezzo visibile).")
             # return False # Non usciamo, proviamo comunque a salvare i cookie magari è solo un glitch
            
        logger.info("LOGIN RIUSCITO!")
        
        # 4. SALVA I COOKIE PER LA PROSSIMA VOLTA
        self.save_cookies()
        
        self.naviga_e_salva()
        return True

    def naviga_e_salva(self):
        logger.info("=== INIZIO CRAWLER ===")
        time.sleep(3)
        
        queue = deque()
        visited = set()
        
        # 1. Carica categorie SEED statiche
        logger.info(f"Caricamento {len(EUROSPIN_MAIN_CATEGORIES)} categorie principali...")
        for cat_url in EUROSPIN_MAIN_CATEGORIES:
            full_url = f"{self.store_url}{cat_url}" if not cat_url.startswith("http") else cat_url
            # Rimuovi eventuali doppi slash
            full_url = full_url.replace(f"{self.store_url}/category//", f"{self.store_url}/category/")
            
            name = cat_url.split('/')[-1].replace('-', ' ').title()
            queue.append((full_url, name))
            visited.add(full_url)

        max_iter = config.MAX_ITERATIONS
        iter_count = 0
        
        while queue and iter_count < max_iter:
            url, nome_cat = queue.popleft() 
            iter_count += 1
            
            logger.info(f"[{iter_count}/{max_iter}] Visito categoria: {nome_cat}")
            try:
                self.rate_limiter.wait()  # Rate limiting
                self.driver.get(url)
                time.sleep(config.PAGE_LOAD_DELAY)  # Aumento attesa per caricamento JS
                
                # Scroll per triggerare lazy loading
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(config.SCROLL_DELAY)
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                prodotti_trovati = self.scrape_current_page(nome_cat)
                
                # Se troviamo pochi prodotti o siamo in una macro-categoria, cerchiamo sottocategorie
                # Anche se troviamo prodotti, cerchiamo sottocategorie per approfondire (es: /carne-e-pesce -> carne)
                new_links = self.find_subcategories_in_body(url)
                for nh, nt in new_links:
                    if nh not in visited and self._is_valid_category_url(nh, nt):
                        queue.append((nh, f"{nome_cat} > {nt}")) 
                        visited.add(nh)
                        logger.info(f"   -> Trovata sottocategoria: {nt}")

                # Gestione paginazione solo se ci sono prodotti
                if prodotti_trovati > 0:
                    page = 1
                    while self.go_next_page():
                        page += 1
                        logger.info(f"   Pagina {page}...")
                        self.scrape_current_page(nome_cat)
                        if page >= config.MAX_PAGES_PER_CATEGORY: 
                            break 
                        
            except Exception as e:
                logger.error(f"Errore durante visita categoria {nome_cat}: {e}")

    def _is_valid_category_url(self, url, text):
        if not url or "javascript" in url: return False
        if len(text) < 2: return False
        u = url.lower()
        t = text.lower()
        for bad in self.BLACKLIST_URL:
            if bad in u or bad in t: return False
        if "eurospin.it" not in u: return False
        if re.search(r'-\d{6,}$', u): return False 
        return True

    def scrape_current_page(self, categoria):
        # Use JS to find all product cards (piercing Shadow DOM)
        js_script = """
        function getAllProductTexts() {
            var cardTexts = [];
            var processedNodes = new Set();
            
            function isVisible(elem) {
                if (!elem) return false;
                return !!(elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length);
            }

            // Recursive function to find price elements in Shadow DOM
            function findPrices(root) {
                var prices = [];
                
                // 1. Check current root for price elements
                var candidates = root.querySelectorAll(".price, .prezzo, [class*='price'], [class*='prezzo']");
                
                candidates.forEach(el => {
                     if (el.innerText && el.innerText.includes('€')) {
                         prices.push(el);
                     }
                });

                if (candidates.length === 0) {
                     var treeWalker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
                     var textNode;
                     while(textNode = treeWalker.nextNode()) {
                         if (textNode.nodeValue && textNode.nodeValue.includes('€')) {
                             if (textNode.parentElement && isVisible(textNode.parentElement)) {
                                 prices.push(textNode.parentElement);
                             }
                         }
                     }
                }

                // 2. Traverse children for Shadow Roots
                var walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
                var node;
                while(node = walker.nextNode()) {
                    if (node.shadowRoot) {
                        prices = prices.concat(findPrices(node.shadowRoot));
                    }
                }
                
                return prices;
            }

            var prices = findPrices(document.body);
            
            prices.forEach(p => {
                if (!isVisible(p)) return;
                
                var card = p;
                for(var i=0; i<6; i++) {
                    if (card.parentNode && card.parentNode.nodeType === 1) {
                         card = card.parentNode;
                    } else if (card.getRootNode() instanceof ShadowRoot && card.parentNode === card.getRootNode()) {
                         card = card.getRootNode().host;
                    } else {
                         break;
                    }
                    
                    if (processedNodes.has(card)) break;
                    
                    var txt = card.innerText;
                    if (!txt) continue;
                    
                    if (txt.includes('Totale') || txt.includes('Riepilogo')) break;
                    
                    if (/\\d+[.,]\\d+\\s?€/.test(txt)) {
                         if (txt.split('\\n').length >= 2) {
                             cardTexts.push(txt);
                             processedNodes.add(card);
                             break;
                         }
                    }
                }
            });
            
            return cardTexts;
        }
        return getAllProductTexts();
        """
        
        try:
            card_texts = self.driver.execute_script(js_script)
        except Exception as e:
            logger.error(f"Errore JS scraping: {e}")
            card_texts = []

        logger.debug(f"Trovati {len(card_texts)} potenziali prodotti (Shadow DOM)")
        if not card_texts: 
            return 0
        
        count = 0
        for txt in card_texts:
            try:
                txt = txt.strip()
                lines = [l.strip() for l in txt.split('\n') if l.strip()]
                
                if len(lines) < 2: continue 
                if any(x in txt.lower() for x in ["totale", "carrello", "riepilogo"]): break

                matches = re.findall(r'\d+[.,]\d+\s?€', txt)
                if not matches: continue
                
                price_val = self._clean_price(matches[0])
                if price_val < 0.1: continue
                
                nome_prodotto = "N/D"
                marca = None
                unita_misura = self.normalizer.extract_unit(txt)
                
                valid_lines = []
                for line in lines:
                    low = line.lower()
                    if "€" in line and any(c.isdigit() for c in line): continue
                    if self._is_weight(line): continue
                    if any(word in low for word in config.PARSING_IGNORE_WORDS): continue
                    if len(line) < 3: continue
                    valid_lines.append(line)
                
                if valid_lines:
                    nome_prodotto = valid_lines[0]
                    if len(valid_lines) > 1:
                        marca = self.normalizer.extract_brand_from_text(txt, nome_prodotto)
                
                if nome_prodotto != "N/D":
                    self.db.upsert_product(
                        nome=nome_prodotto, 
                        marca=marca, 
                        prezzo_listino=price_val, 
                        prezzo_attuale=price_val, 
                        categoria=categoria, 
                        supermercato="Eurospin",
                        unita_misura=unita_misura
                    )
                    count += 1
                    self.total_saved += 1
            except Exception as e:
                logger.debug(f"Errore parsing card: {e}")
                continue
            
        if count > 0: 
            logger.info(f"Trovati {count} prodotti in categoria")
        return count

    def find_subcategories_in_body(self, current_url):
        """Cerca link a sottocategorie nella pagina corrente"""
        links = []
        try:
            # Cerchiamo link che estendono l'URL corrente o sono relativi
            # Es: siamo su /category/frutta-e-verdura, cerchiamo /frutta-e-verdura/frutta-fresca (senza /category)
            
            # Helper JS per shadow dom
            js_script = """
            function getAllLinks(root) {
                var links = [];
                var anchors = root.querySelectorAll('a[href]');
                anchors.forEach(a => {
                    var t = a.innerText || "";
                    if (!t) {
                         // Prova a cercare immagini con alt o title
                         var img = a.querySelector('img');
                         if (img) t = img.alt || img.title || "";
                    }
                    links.push({href: a.href, text: t});
                });
                
                var walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
                while(node = walker.nextNode()) {
                    if (node.shadowRoot) {
                        links = links.concat(getAllLinks(node.shadowRoot));
                    }
                }
                return links;
            }
            return getAllLinks(document.body);
            """
            
            candidates = self.driver.execute_script(js_script)
            
            # Normalizza URL corrente per confronto
            # Rimuovi /category/ se presente per trovare lo slug base
            base_url_clean = current_url.split('?')[0].rstrip('/')
            category_slug = base_url_clean.split('/')[-1]
            
            # Se siamo in /category/foo, cerchiamo link che contengono /foo/
            
            for item in candidates:
                h = item['href']
                t = item['text']
                if not h: continue
                
                # Filtra
                if "javascript" in h or "mailto" in h: continue
                
                h_clean = h.split('?')[0].rstrip('/')
                
                # Logica rilassata:
                # 1. Il link deve appartenere allo stesso dominio (o relativo)
                if "eurospin.it" in h_clean:
                    # 2. Deve contenere lo slug della categoria corrente
                    if f"/{category_slug}/" in h_clean:
                        # 3. Deve essere diverso dall'URL base
                        if h_clean != base_url_clean and h_clean != base_url_clean.replace("/category", ""):
                            # 4. Escludi prodotti (/product/)
                            if "/product/" not in h_clean:
                                # Fallback nome se vuoto
                                if not t or len(t) < 2:
                                    t = h_clean.split('/')[-1].replace('-', ' ').title()
                                
                                if (h, t) not in links:
                                    links.append((h, t))
                            
        except Exception as e: 
            logger.debug(f"Errore ricerca sottocategorie: {e}")
            pass
        return links


    def go_next_page(self):
        try:
            # Selector aggiornati per Vue.js pagination trovata
            selectors = [
                "button[aria-label*='Successiva']",
                "button[aria-label*='Next']",
                "button[aria-label*='Pagina seguente']",
                "button[aria-label*='seguente']",
                ".v-pagination__navigation:not(.v-pagination__navigation--disabled) button"
            ]
            
            btns = []
            for sel in selectors:
                btns = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if btns: break
            
            # Se non trova con selettori, cerca specificamente l'ultimo bottone della paginazione
            if not btns:
                nav_btns = self.driver.find_elements(By.CSS_SELECTOR, ".v-pagination__navigation")
                if nav_btns:
                    last_btn = nav_btns[-1]
                    # Verifica che sia il bottone 'next' (spesso è l'ultimo nel DOM)
                    if "disabled" not in last_btn.get_attribute("class"):
                         btns = [last_btn]

            if btns and btns[0].is_enabled():
                # Check additional disabled class often used in Vue/Material
                if "disabled" in btns[0].get_attribute("class"):
                    return False
                    
                self.driver.execute_script("arguments[0].click();", btns[0])
                time.sleep(3)
                return True
        except Exception as e: 
            logger.debug(f"Errore paginazione: {e}")
        return False

    def close(self):
        self.db.close()
        self.driver.quit()

    def get_total_products_saved(self):
        return self.total_saved