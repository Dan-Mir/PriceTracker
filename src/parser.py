from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import pickle
import os
from collections import deque
from db import PriceDatabase

class EurospinParser:
    def __init__(self):
        self.store_url = "https://laspesaonline.eurospin.it"
        self.db = PriceDatabase()
        self.cookie_file = "cookies.pkl" # File dove salviamo la sessione
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Parole da ignorare nei link
        self.BLACKLIST_URL = [
            "faq", "assistenza", "contatti", "privacy", "cookie", "policy", 
            "login", "registrati", "volantino", "negozi", "store", "chi-siamo", 
            "lavora-con-noi", "servizio-clienti", "informativa", "condizioni", 
            "ritiro", "consegna", "pagamenti", "home", "aiuto", "scrivici",
            "social", "facebook", "instagram", "app", "dove-siamo", "javascript",
            "carrello", "checkout", "profile"
        ]

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
        print("   🍪 Sessione completa salvata (cookie + storage)!")

    def load_cookies(self):
        """Carica cookie + localStorage + sessionStorage salvati"""
        if not os.path.exists(self.cookie_file):
            print("   ⚠️ Nessun file sessione trovato.")
            return False
        
        try:
            with open(self.cookie_file, 'rb') as file:
                session_data = pickle.load(file)
                
                # GESTISCI RETROCOMPATIBILITÀ: se è una lista, sono vecchi cookie
                if isinstance(session_data, list):
                    print("   ⚠️ File cookie vecchio formato - richiesto nuovo login")
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
                
            print("   🍪 Sessione ripristinata (cookie + localStorage + sessionStorage)")
            return True
        except Exception as e:
            print(f"   ❌ Errore ripristino sessione: {e}")
            return False
    
    def _verifica_sessione_valida(self):
        """Verifica se la sessione corrente mostra i prezzi (sessione valida)"""
        try:
            # Visita una pagina prodotti nota per testare
            test_url = f"{self.store_url}/frutta-e-verdura"
            print("   🔍 Verifico validità sessione...")
            self.driver.get(test_url)
            time.sleep(4)
            
            # Scroll per triggerare lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Cerco prezzi sulla pagina
            prices = self.driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
            if not prices:
                prices = self.driver.find_elements(By.CSS_SELECTOR, ".price, .prezzo, [class*='price'], [class*='prezzo']")
            
            if len(prices) > 0:
                print(f"   ✅ Sessione valida - {len(prices)} prezzi visibili")
                return True
            else:
                print("   ❌ Sessione non valida - nessun prezzo visibile")
                return False
        except Exception as e:
            print(f"   ⚠️ Errore verifica sessione: {e}")
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
        print("\n🔐 --- INIZIO LOGIN ---")
        
        # 1. Naviga sul dominio (necessario prima di caricare i cookie)
        self.driver.get(self.store_url)
        time.sleep(2)

        # 2. TENTA LOGIN CON COOKIE
        if self.load_cookies():
            # Dopo aver caricato i cookie, vai direttamente sulla pagina di test
            # SENZA fare refresh (che potrebbe invalidare i cookie)
            if self._verifica_sessione_valida():
                print("   🎉 SESSIONE RIPRISTINATA! Salto il login manuale.")
                self.naviga_e_salva()
                return True
            else:
                print("   ⚠️ Cookie presenti ma sessione scaduta. Elimino cookie e rifaccio login.")
                # Elimina cookie non validi
                if os.path.exists(self.cookie_file):
                    os.remove(self.cookie_file)
                    print("   🗑️ Cookie eliminati.")
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
            print("   ❌ Errore: Icona profilo non trovata.")
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
            print("   ❌ Errore: Campo email non trovato.")
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
        
        print("   (Wait) Attendo login...")
        time.sleep(8)
        if "identity.eurospin" in self.driver.current_url:
            print("   ⚠️ Login forse fallito.")
            return False
            
        print("   🎉 LOGIN RIUSCITO!")
        
        # 4. SALVA I COOKIE PER LA PROSSIMA VOLTA
        self.save_cookies()
        
        self.naviga_e_salva()
        return True

    def naviga_e_salva(self):
        print("\n🥦 --- INIZIO CRAWLER ---")
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
            
            print(f"   ✅ Coda iniziale: {len(queue)} categorie.")
        except Exception as e:
            print(f"   ❌ Errore menu: {e}")

        max_iter = 60 
        iter_count = 0
        
        while queue and iter_count < max_iter:
            url, nome_cat = queue.popleft() 
            iter_count += 1
            
            print(f"\n   🚀 [{iter_count}/{max_iter}] Visito: {nome_cat}")
            try:
                self.driver.get(url)
                time.sleep(5)  # Aumento attesa per caricamento JS
                
                # Scroll per triggerare lazy loading
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
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
                        print(f"      📄 Pagina {page}...")
                        self.scrape_current_page(nome_cat)
                        if page >= 15: break 
                        
            except Exception as e:
                print(f"      ⚠️ Errore visita: {e}")

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
        # Provo diversi selettori per trovare i prezzi
        prices = self.driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
        
        # Se XPath fallisce, provo con CSS selectors comuni
        if not prices:
            prices = self.driver.find_elements(By.CSS_SELECTOR, ".price, .prezzo, [class*='price'], [class*='prezzo']")
        
        print(f"      🔍 Trovati {len(prices)} elementi con €")
        if not prices: return 0
        
        count = 0
        processed_cards = []
        
        for p in prices:
            if not p.is_displayed(): continue
            try:
                card = p
                # Risalita intelligente
                for _ in range(6):
                    try: card = card.find_element(By.XPATH, "./..")
                    except: break
                    
                    if card in processed_cards: break
                    
                    txt = card.text.strip()
                    lines = [l.strip() for l in txt.split('\n') if l.strip()]
                    
                    if len(lines) < 2: continue 
                    if any(x in txt.lower() for x in ["totale", "carrello", "riepilogo"]): break

                    matches = re.findall(r'\d+[.,]\d+\s?€', txt)
                    if not matches: continue
                    price_val = self._clean_price(matches[0])
                    if price_val < 0.1: break 
                    
                    nome_prodotto = "N/D"
                    marca = ""  # Marca vuota per ora, da implementare estrazione
                    
                    for line in lines:
                        low = line.lower()
                        if "€" in line and any(c.isdigit() for c in line): continue
                        if self._is_weight(line): continue
                        if "aggiungi" in low or "al kg" in low or "al pz" in low: continue
                        if len(line) < 3: continue
                        
                        # Euristiche per capire se è una marca (spesso in maiuscolo o breve)
                        # Per ora prendiamo la prima riga valida come nome prodotto
                        nome_prodotto = line
                        
                        # TODO: Implementare estrazione marca dalle righe successive
                        break
                    
                    if nome_prodotto != "N/D":
                        print(f"      💾 Salvo: {nome_prodotto} - €{price_val}")
                        self.db.insert_product(nome_prodotto, marca, price_val, price_val, categoria, "Eurospin")
                        
                        processed_cards.append(card)
                        count += 1
                        break 
            except Exception as e:
                print(f"      ⚠️ Errore parsing card: {e}")
                continue
            
        if count > 0: print(f"      ✅ Trovati {count} prodotti.")
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