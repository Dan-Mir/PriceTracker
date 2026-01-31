"""
Esplora la struttura del menu Castoro per trovare tutte le sottocategorie
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import platform

# Setup driver
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

if platform.machine() in ['aarch64', 'armv7l', 'arm64']:
    options.binary_location = '/usr/bin/chromium'
    service = Service(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
else:
    driver = webdriver.Chrome(options=options)

try:
    print("🔍 Caricamento homepage...")
    driver.get("https://www.castoro.shop")
    time.sleep(10)  # Più tempo per caricamento
    
    # Rimuovi cookie banner
    driver.execute_script("""
        var banner = document.getElementById('iubenda-cs-banner');
        if (banner) banner.remove();
    """)
    time.sleep(2)
    
    # Salva screenshot prima di aprire menu
    driver.save_screenshot("castoro_before_menu.png")
    print("Screenshot pre-menu: castoro_before_menu.png")
    
    # Cerca il pulsante PRODOTTI - potrebbe essere diverso
    print("\n🔍 Ricerca pulsante menu...")
    
    # Prova diversi selettori
    menu_selectors = [
        "//button[contains(., 'PRODOTTI')]",
        "//button[contains(text(), 'PRODOTTI')]",
        "//div[contains(text(), 'PRODOTTI')]",
        "//a[contains(text(), 'PRODOTTI')]",
        "//button[contains(@class, 'menu')]",
        "//*[contains(text(), 'PRODOTTI')]"
    ]
    
    menu_button = None
    for selector in menu_selectors:
        try:
            menu_button = driver.find_element(By.XPATH, selector)
            print(f"✅ Trovato con: {selector}")
            break
        except:
            continue
    
    if not menu_button:
        # Stampa tutti i bottoni visibili
        print("\n⚠️  Pulsante PRODOTTI non trovato. Bottoni disponibili:")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons[:10]:
            print(f"  • {btn.text[:50]}")
        
        # Salva HTML per debug
        with open("castoro_debug.html", "w") as f:
            f.write(driver.page_source)
        print("\nHTML salvato in castoro_debug.html")
        driver.quit()
        exit(1)
    
    # Clicca sul menu PRODOTTI
    print("\n📱 Apertura menu PRODOTTI...")
    menu_button.click()
    time.sleep(4)
    
    # Salva screenshot del menu aperto
    driver.save_screenshot("castoro_menu_aperto.png")
    print("Screenshot salvato: castoro_menu_aperto.png")
    
    # Trova tutte le categorie principali (quelle con la freccia >)
    print("\n📂 CATEGORIE PRINCIPALI E SOTTOCATEGORIE:\n")
    print("=" * 80)
    
    main_categories = driver.find_elements(By.XPATH, "//div[contains(@class, 'list-item')]")
    
    all_subcategories = {}
    
    for i, main_cat in enumerate(main_categories, 1):
        try:
            # Nome categoria principale
            cat_name = main_cat.text.strip().split('\n')[0]
            
            if not cat_name or cat_name == '':
                continue
                
            print(f"\n{i}. {cat_name}")
            print("-" * 80)
            
            # Clicca sulla categoria per aprirla
            main_cat.click()
            time.sleep(2)
            
            # Cerca sottocategorie (link arancioni)
            # Le sottocategorie dovrebbero essere link con class che contiene "orange" o simili
            subcats = driver.find_elements(By.XPATH, "//a[contains(@class, 'subtitle') or contains(@class, 'link')]")
            
            # Oppure cerca tutti i link visibili nel menu
            all_links = driver.find_elements(By.XPATH, "//div[contains(@class, 'menu')]//a[@href]")
            
            subcategories = []
            for link in all_links:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                if href and 'category' in href and text:
                    subcategories.append({
                        'name': text,
                        'url': href
                    })
                    print(f"   → {text}")
                    print(f"      {href}")
            
            all_subcategories[cat_name] = subcategories
            
            # Torna indietro (chiudi sottomenu)
            # Cerca pulsante "indietro" o riclicca la categoria
            try:
                back_button = driver.find_element(By.XPATH, "//button[contains(@class, 'back')]")
                back_button.click()
                time.sleep(1)
            except:
                # Se non c'è back, riapri il menu
                menu_button = driver.find_element(By.XPATH, "//button[contains(., 'PRODOTTI')]")
                menu_button.click()
                time.sleep(2)
                
        except Exception as e:
            print(f"   ⚠️  Errore: {e}")
            continue
    
    # Riepilogo
    print("\n" + "=" * 80)
    print("📊 RIEPILOGO TOTALE")
    print("=" * 80)
    
    total_subcats = sum(len(subs) for subs in all_subcategories.values())
    print(f"\nCategorie principali: {len(all_subcategories)}")
    print(f"Sottocategorie totali: {total_subcats}")
    
    print("\n📋 LISTA COMPLETA SOTTOCATEGORIE:")
    for main_cat, subs in all_subcategories.items():
        print(f"\n{main_cat}: {len(subs)} sottocategorie")
        for sub in subs:
            print(f"  • {sub['name']}")

finally:
    driver.quit()
