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
from ..db import PriceDatabase
from ..logger import get_logger
from ..normalizer import ProductNormalizer
from ..utils import retry_on_exception, RateLimiter
from .. import config

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
            test_url = f"{self.store_url}/frutta-e-verdura"
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
            self.driver.execute_script("document.querySelector('.icon-profile').click();")
        except:
            logger.error("Icona profilo non trovata")
            return False
        
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
        if "identity.eurospin" in self.driver.current_url:
            logger.warning("Login probabilmente fallito")
            return False
            
        logger.info("LOGIN RIUSCITO!")
        
        # 4. SALVA I COOKIE PER LA PROSSIMA VOLTA
        self.save_cookies()
        
        self.naviga_e_salva()
        return True

    def naviga_e_salva(self):
        logger.info("=== INIZIO CRAWLER ===")
        time.sleep(3)
        
        try:
            self.driver.execute_script("var b=document.querySelector('.icon-menu')||document.querySelector('button');if(b)b.click();")
            time.sleep(2)
        except: pass

        queue = deque()
        visited = set()
        
        # Recupero categorie iniziali dal menu
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "nav.v-navigation-drawer .category2 a")
            main_links = self.driver.find_elements(By.CSS_SELECTOR, "nav.v-navigation-drawer a.menu-link")
            
            for l in links + main_links:
                h = l.get_attribute("href")
                t = l.get_attribute("innerText").strip()
                if self._is_valid_category_url(h, t):
                    if h not in visited:
                        queue.append((h, t))
                        visited.add(h)
            
            logger.info(f"Coda iniziale: {len(queue)} categorie")
        except Exception as e:
            logger.error(f"Errore recupero menu: {e}")

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
                
                if prodotti_trovati < 2:
                    new_links = self.find_subcategories_in_body()
                    added = 0
                    for nh, nt in new_links:
                        if nh not in visited and self._is_valid_category_url(nh, nt):
                            queue.append((nh, f"{nome_cat} > {nt}")) 
                            visited.add(nh)
                            added += 1
                else:
                    page = 1
                    while self.go_next_page():
                        page += 1
                        logger.info(f"   Pagina {page}...")
                        self.scrape_current_page(nome_cat)
                        if page >= config.MAX_PAGES_PER_CATEGORY: 
                            break 
                        
            except Exception as e:
                logger.error(f"Errore durante visita categoria: {e}")

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
                // Try selectors first
                var candidates = root.querySelectorAll(".price, .prezzo, [class*='price'], [class*='prezzo']");
                
                candidates.forEach(el => {
                     if (el.innerText && el.innerText.includes('€')) {
                         prices.push(el);
                     }
                });

                // Also check generic elements if they contain € (fallback)
                if (candidates.length === 0) {
                     // Limit this to leaf nodes to avoid huge duplicates
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
                // Go up levels to find the card container
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
                    
                    // Filter out non-card text
                    if (txt.includes('Totale') || txt.includes('Riepilogo')) break;
                    
                    // Must contain a price pattern
                    if (/\\d+[.,]\\d+\\s?€/.test(txt)) {
                         // Must have multiple lines (Name, Price, etc.)
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
                
                if len(lines) < 2: 
                    continue 
                if any(x in txt.lower() for x in ["totale", "carrello", "riepilogo"]): 
                    break

                matches = re.findall(r'\d+[.,]\d+\s?€', txt)
                if not matches: 
                    continue
                    price_val = self._clean_price(matches[0])
                    if price_val < 0.1: 
                        break 
                    
                    # Estrazione intelligente nome, marca e unità
                    nome_prodotto = "N/D"
                    marca = None
                    unita_misura = None
                    
                    # Estrai unità misura dal testo completo
                    unita_misura = self.normalizer.extract_unit(txt)
                    
                    # Processa le linee per estrarre nome e marca
                    valid_lines = []
                    for line in lines:
                        low = line.lower()
                        # Salta linee con prezzi, parole chiave inutili o troppo corte
                        if "€" in line and any(c.isdigit() for c in line): 
                            continue
                        if self._is_weight(line): 
                            continue
                        if any(word in low for word in config.PARSING_IGNORE_WORDS): 
                            continue
                        if len(line) < 3: 
                            continue
                        
                        valid_lines.append(line)
                    
                    # Estrai nome prodotto (prima linea valida)
                    if valid_lines:
                        nome_prodotto = valid_lines[0]
                        
                        # Tenta estrazione marca (seconda linea se esiste)
                        if len(valid_lines) > 1:
                            # Usa il normalizzatore per estrarre la marca
                            marca = self.normalizer.extract_brand_from_text(txt, nome_prodotto)
                    
                    if nome_prodotto != "N/D":
                        logger.debug(f"Salvo: {nome_prodotto} [{marca or 'N/D'}] [{unita_misura or 'N/D'}] - €{price_val}")
                        self.db.upsert_product(
                            nome=nome_prodotto, 
                            marca=marca, 
                            prezzo_listino=price_val, 
                            prezzo_attuale=price_val, 
                            categoria=categoria, 
                            supermercato="Eurospin",
                            unita_misura=unita_misura
                        )
                        
                        processed_cards.append(card)
                        count += 1
                        break 
            except Exception as e:
                logger.debug(f"Errore parsing card: {e}")
                continue
            
        if count > 0: 
            logger.info(f"Trovati {count} prodotti in categoria")
        return count

    def find_subcategories_in_body(self):
        links = []
        try:
            candidates = self.driver.find_elements(By.CSS_SELECTOR, ".v-main a[href]")
            for l in candidates:
                if not l.is_displayed(): continue
                h = l.get_attribute("href")
                t = l.get_attribute("innerText").strip()
                if self._is_valid_category_url(h, t):
                    if (h, t) not in links:
                        links.append((h, t))
        except: pass
        return links

    def go_next_page(self):
        try:
            btns = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Successiva'], button[aria-label*='Next']")
            if not btns:
                btns = self.driver.find_elements(By.CSS_SELECTOR, ".v-pagination .mdi-chevron-right")
                if btns: btns = [btns[0].find_element(By.XPATH, "./..")]
            
            if btns and btns[0].is_enabled() and "disabled" not in btns[0].get_attribute("class"):
                self.driver.execute_script("arguments[0].click();", btns[0])
                time.sleep(3)
                return True
        except: pass
        return False

    def close(self):
        self.db.close()
        self.driver.quit()