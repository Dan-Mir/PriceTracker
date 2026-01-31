#!/usr/bin/env python3
"""
Test esplorativo per analizzare la struttura del sito Castoro
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import platform

def explore_castoro():
    """Esplora la struttura del sito Castoro"""
    
    print("🔍 Avvio esplorazione Castoro Shop...")
    print("=" * 70)
    
    # Setup driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # ARM detection
    if platform.machine() in ['aarch64', 'armv7l', 'arm64']:
        print("✅ ARM detectato, uso Chromium")
        options.binary_location = '/usr/bin/chromium'
        from selenium.webdriver.chrome.service import Service
        service = Service(executable_path='/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    
    try:
        # 1. Carica homepage
        url = "https://www.castoro.shop"
        print(f"\n📄 Caricamento: {url}")
        driver.get(url)
        
        # Aspetta caricamento SPA
        time.sleep(5)
        
        print(f"✅ Titolo pagina: {driver.title}")
        print(f"✅ URL attuale: {driver.current_url}")
        
        # 1.5 Chiudi banner cookie se presente
        print("\n🍪 Gestione cookie banner...")
        try:
            # Rimuovi il banner con JavaScript
            driver.execute_script("""
                var banner = document.getElementById('iubenda-cs-banner');
                if (banner) {
                    banner.remove();
                    console.log('Banner removed');
                }
            """)
            time.sleep(1)
            print("  ✅ Cookie banner rimosso con JavaScript")
        except Exception as e:
            print(f"  ⚠️  Nessun banner cookie trovato (ok)")
        
        # 2. Cerca il burger menu "PRODOTTI"
        print("\n🍔 Ricerca burger menu...")
        
        # Possibili selettori
        selectors = [
            "//button[contains(text(), 'PRODOTTI')]",
            "//a[contains(text(), 'PRODOTTI')]",
            "//div[contains(@class, 'menu')]//button",
            "//button[contains(@class, 'burger')]",
            "//button[contains(@class, 'v-app-bar__nav-icon')]",
            "//i[contains(@class, 'mdi-menu')]",
        ]
        
        menu_button = None
        for selector in selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"  ✅ Trovato con: {selector}")
                    print(f"     Elementi: {len(elements)}")
                    for i, elem in enumerate(elements[:3]):
                        print(f"       {i+1}. Text: '{elem.text}' | Tag: {elem.tag_name} | Class: {elem.get_attribute('class')}")
                    menu_button = elements[0]
                    break
            except Exception as e:
                pass
        
        if not menu_button:
            print("  ❌ Burger menu non trovato, cerco direttamente categorie...")
            
            # Cerca categorie visibili
            cat_selectors = [
                "//a[contains(@href, '/category/')]",
                "//div[contains(@class, 'category')]",
                "//nav//a",
            ]
            
            for selector in cat_selectors:
                try:
                    cats = driver.find_elements(By.XPATH, selector)
                    if cats:
                        print(f"\n📂 Categorie trovate ({len(cats)}):")
                        for i, cat in enumerate(cats[:10]):
                            print(f"  {i+1}. {cat.text} | href: {cat.get_attribute('href')}")
                except:
                    pass
        else:
            # Clicca sul menu
            print("\n🖱️  Click sul burger menu...")
            menu_button.click()
            time.sleep(2)
            
            # Cerca categorie apparse
            print("\n📂 Ricerca categorie nel menu...")
            cat_selectors = [
                "//div[contains(@class, 'v-navigation-drawer')]//a",
                "//aside//a[contains(@href, 'category')]",
                "//nav//a",
                "//div[contains(@class, 'category')]//a",
            ]
            
            for selector in cat_selectors:
                try:
                    cats = driver.find_elements(By.XPATH, selector)
                    if cats:
                        print(f"\n  ✅ Trovate con {selector}:")
                        for i, cat in enumerate(cats[:15]):
                            text = cat.text.strip()
                            href = cat.get_attribute('href')
                            if text or href:
                                print(f"    {i+1}. '{text}' → {href}")
                except Exception as e:
                    pass
        
        # 3. Prova a cercare prodotti in evidenza
        print("\n🛒 Ricerca prodotti in homepage...")
        
        prod_selectors = [
            "//div[contains(@class, 'product')]",
            "//article[contains(@class, 'card')]",
            "//div[contains(@class, 'v-card')]",
        ]
        
        for selector in prod_selectors:
            try:
                prods = driver.find_elements(By.XPATH, selector)
                if prods:
                    print(f"\n  ✅ Prodotti con {selector}: {len(prods)}")
                    
                    # Analizza primo prodotto
                    if prods:
                        prod = prods[0]
                        print(f"\n  📦 Primo prodotto:")
                        print(f"     HTML: {prod.get_attribute('innerHTML')[:300]}...")
                        
                        # Cerca nome
                        try:
                            nome = prod.find_element(By.XPATH, ".//h3 | .//h4 | .//div[contains(@class, 'title')]")
                            print(f"     Nome: {nome.text}")
                        except:
                            pass
                        
                        # Cerca prezzo
                        try:
                            prezzo = prod.find_element(By.XPATH, ".//*[contains(text(), '€')]")
                            print(f"     Prezzo: {prezzo.text}")
                        except:
                            pass
                    
                    break
            except Exception as e:
                pass
        
        # 4. Salva screenshot
        print("\n📸 Salvo screenshot...")
        driver.save_screenshot('castoro_homepage.png')
        print("  ✅ Salvato: castoro_homepage.png")
        
        # 5. Salva HTML completo
        with open('castoro_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("  ✅ Salvato: castoro_page_source.html")
        
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("\n✅ Browser chiuso")


if __name__ == "__main__":
    explore_castoro()
