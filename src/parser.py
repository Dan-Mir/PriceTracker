from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from collections import deque
from db import PriceDatabase

class EurospinParser:
    def __init__(self):
        self.store_url = "https://laspesaonline.eurospin.it"
        self.db = PriceDatabase()
        
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

    def _clean_price(self, price_str):
        if not price_str: return 0.0
        clean = price_str.replace('€', '').replace(' ', '').replace(',', '.')
        try:
            val = float(re.findall(r"[-+]?\d*\.\d+|\d+", clean)[0])
            return val
        except:
            return 0.0

    def _is_weight(self, text):
        """Ritorna True se la stringa sembra un peso (es. 200g, 1kg, 500ml)"""
        # Regex per pesi comuni
        pattern = r'^\d+\s*[.,]?\s*\d*\s*(g|kg|ml|l|lt|cl|pz|pezz[oi])\s*e?$'
        return re.match(pattern, text.strip(), re.IGNORECASE) is not None

    def login_interattivo(self, email):
        print("\n🔐 --- INIZIO LOGIN ---")
        self.driver.get(self.store_url)
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
        self.naviga_e_salva()
        return True

    def naviga_e_salva(self):
        print("\n🥦 --- INIZIO CRAWLER V5 (Smart Filtering) ---")
        time.sleep(3)
        
        try:
            self.driver.execute_script("var b=document.querySelector('.icon-menu')||document.querySelector('button');if(b)b.click();")
            time.sleep(2)
        except: pass

        queue = deque()
        visited = set()
        
        # 1. Recupero Categorie Iniziali
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

        # 2. Crawler Loop
        max_iter = 50 # Aumentato per coprire più terreno
        iter_count = 0
        
        while queue and iter_count < max_iter:
            url, nome_cat = queue.popleft() 
            iter_count += 1
            
            print(f"\n   🚀 [{iter_count}/{max_iter}] Visito: {nome_cat}")
            try:
                self.driver.get(url)
                time.sleep(3)
                
                # A. Scraping Prodotti
                prodotti_trovati = self.scrape_current_page(nome_cat)
                
                # B. Se è una pagina "di snodo" (pochi prodotti, forse categorie)
                if prodotti_trovati < 2:
                    new_links = self.find_subcategories_in_body()
                    added = 0
                    for nh, nt in new_links:
                        if nh not in visited and self._is_valid_category_url(nh, nt):
                            queue.append((nh, f"{nome_cat} > {nt}")) 
                            visited.add(nh)
                            added += 1
                    
                    if added > 0:
                        print(f"      🔗 Aggiunte {added} sottocategorie.")
                    else:
                        print("      ⚠️ Nessun prodotto e nessuna sottocategoria.")
                else:
                    # C. Paginazione (Solo se è una pagina prodotti vera)
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
        
        # CRUCIALE: Evitiamo URL che sembrano prodotti specifici
        # Spesso hanno pattern numerici complessi o /p/ invece di /c/
        # Eurospin url: .../frutta-e-verdura (ok) vs .../frutta-e-verdura/banane-12345 (no)
        # Se l'URL finisce con un codice numerico lungo, spesso è un prodotto
        if re.search(r'-\d{6,}$', u): return False 
        
        return True

    def scrape_current_page(self, categoria):
        # Cerca card che contengono prezzo
        prices = self.driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
        if not prices: return 0
        
        count = 0
        processed_cards = []
        
        for p in prices:
            if not p.is_displayed(): continue
            try:
                card = p
                # Risalita intelligente: cerchiamo un contenitore che abbia senso
                for _ in range(6):
                    try: card = card.find_element(By.XPATH, "./..")
                    except: break
                    
                    if card in processed_cards: break
                    
                    txt = card.text.strip()
                    lines = [l.strip() for l in txt.split('\n') if l.strip()]
                    
                    if len(lines) < 2: continue 
                    
                    # Se c'è scritto "Totale", "Carrello" -> scarta
                    if any(x in txt.lower() for x in ["totale", "carrello", "riepilogo"]): break

                    # Check prezzo
                    matches = re.findall(r'\d+[.,]\d+\s?€', txt)
                    if not matches: continue
                    price_val = self._clean_price(matches[0])
                    if price_val < 0.1: break 
                    
                    # ESTRAZIONE NOME MIGLIORATA
                    nome_prodotto = "N/D"
                    for line in lines:
                        low = line.lower()
                        # Scarta se: è prezzo, è peso, è "aggiungi", è "al kg"
                        if "€" in line and any(c.isdigit() for c in line): continue
                        if self._is_weight(line): continue
                        if "aggiungi" in low or "al kg" in low or "al pz" in low: continue
                        if len(line) < 3: continue
                        
                        # Se sopravvive, è il nome (o la marca)
                        nome_prodotto = line
                        break
                    
                    if nome_prodotto != "N/D":
                        # print(f"DEBUG: {nome_prodotto} - {price_val}")
                        self.db.insert_product(nome_prodotto, "Eurospin", price_val, price_val, categoria)
                        processed_cards.append(card)
                        count += 1
                        break 
            except: continue
            
        if count > 0: print(f"      ✅ Trovati {count} prodotti.")
        return count

    def find_subcategories_in_body(self):
        links = []
        try:
            # Cerchiamo link nel corpo, MA ESCLUDIAMO quelli dentro le card prodotto
            # Strategia: cerchiamo i link, poi controlliamo se il loro genitore ha un prezzo "vicino"
            candidates = self.driver.find_elements(By.CSS_SELECTOR, ".v-main a[href]")
            
            for l in candidates:
                if not l.is_displayed(): continue
                h = l.get_attribute("href")
                t = l.get_attribute("innerText").strip()
                
                # Controllo se è una categoria valida
                if self._is_valid_category_url(h, t):
                    # Check Extra: Se il link contiene un'immagine piccola, o testo "Aggiungi" vicino..
                    # Per semplicità, ci fidiamo del filtro regex sugli URL
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