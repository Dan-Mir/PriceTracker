"""
Test esplorativo per capire la struttura del sito Castoro
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import platform

# Setup browser
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36')

if platform.machine() in ['aarch64', 'armv7l', 'arm64']:
    options.binary_location = '/usr/bin/chromium'
    from selenium.webdriver.chrome.service import Service
    service = Service(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
else:
    driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 20)

print("🔍 TEST ESPLORATIVO CASTORO SHOP")
print("=" * 60)

try:
    # 1. Homepage
    print("\n1. Caricamento homepage...")
    driver.get("https://www.castoroeshop.it")
    time.sleep(5)
    
    print(f"   Title: {driver.title}")
    print(f"   URL: {driver.current_url}")
    
    # Salva screenshot
    driver.save_screenshot("/home/danym/Desktop/supermarket_parser/test_castoro_homepage.png")
    print("   Screenshot salvato: test_castoro_homepage.png")
    
    # 2. Cerca menu PRODOTTI
    print("\n2. Ricerca menu PRODOTTI...")
    
    try:
        # Prova diversi selettori
        menu_selectors = [
            "//button[contains(text(), 'PRODOTTI')]",
            "//button[contains(., 'PRODOTTI')]",
            "//a[contains(text(), 'PRODOTTI')]",
            "//div[contains(@class, 'menu')]//button",
            "//*[contains(text(), 'Prodotti')]",
        ]
        
        menu_button = None
        for selector in menu_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"   ✅ Trovato con: {selector}")
                    print(f"      Elementi: {len(elements)}")
                    for i, elem in enumerate(elements[:3]):
                        print(f"      [{i}] Text: '{elem.text}' | Tag: {elem.tag_name}")
                    menu_button = elements[0]
                    break
            except Exception as e:
                continue
        
        if menu_button:
            print("\n3. Click su menu PRODOTTI...")
            menu_button.click()
            time.sleep(3)
            
            driver.save_screenshot("/home/danym/Desktop/supermarket_parser/test_castoro_menu.png")
            print("   Screenshot menu salvato: test_castoro_menu.png")
            
            # 4. Cerca categorie
            print("\n4. Ricerca categorie...")
            
            category_selectors = [
                "//div[contains(@class, 'category')]//a",
                "//div[contains(@class, 'menu')]//a",
                "//a[contains(@href, '/c/')]",
                "//ul//li//a",
            ]
            
            for selector in category_selectors:
                categories = driver.find_elements(By.XPATH, selector)
                if categories:
                    print(f"   ✅ Trovate {len(categories)} categorie con: {selector}")
                    for i, cat in enumerate(categories[:10]):
                        try:
                            print(f"      [{i}] {cat.text} → {cat.get_attribute('href')}")
                        except:
                            pass
                    break
        else:
            print("   ❌ Menu PRODOTTI non trovato")
            
            # Stampa tutti i link visibili
            print("\n   Link visibili sulla pagina:")
            links = driver.find_elements(By.TAG_NAME, "a")
            for i, link in enumerate(links[:20]):
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')
                    if text:
                        print(f"      [{i}] {text} → {href}")
                except:
                    pass
    
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    # 5. Prova una categoria hardcoded
    print("\n5. Test navigazione categoria diretta...")
    test_url = "https://www.castoroeshop.it/c/frutta-e-verdura"
    print(f"   URL: {test_url}")
    
    driver.get(test_url)
    time.sleep(5)
    
    driver.save_screenshot("/home/danym/Desktop/supermarket_parser/test_castoro_categoria.png")
    print("   Screenshot categoria salvato: test_castoro_categoria.png")
    
    # Cerca prodotti
    print("\n6. Ricerca prodotti nella categoria...")
    
    product_selectors = [
        "//div[contains(@class, 'product')]",
        "//div[contains(@class, 'item')]",
        "//div[contains(@class, 'card')]",
        "//*[contains(@class, 'price')]",
    ]
    
    for selector in product_selectors:
        products = driver.find_elements(By.XPATH, selector)
        if products:
            print(f"   ✅ Trovati {len(products)} elementi con: {selector}")
            
            # Analizza primo prodotto
            if products:
                print("\n   Analisi primo elemento:")
                first = products[0]
                print(f"      HTML: {first.get_attribute('outerHTML')[:200]}...")
                print(f"      Text: {first.text[:100]}")
                
                # Cerca nome
                try:
                    name = first.find_element(By.XPATH, ".//h2 | .//h3 | .//*[contains(@class, 'title')]")
                    print(f"      Nome: {name.text}")
                except:
                    print("      Nome: non trovato")
                
                # Cerca prezzo
                try:
                    price = first.find_element(By.XPATH, ".//*[contains(@class, 'price')]")
                    print(f"      Prezzo: {price.text}")
                except:
                    print("      Prezzo: non trovato")
            
            break
    
    print("\n" + "=" * 60)
    print("✅ Test completato!")
    print("\nGuarda gli screenshot per capire la struttura:")
    print("  - test_castoro_homepage.png")
    print("  - test_castoro_menu.png")
    print("  - test_castoro_categoria.png")

except Exception as e:
    print(f"\n❌ Errore: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
