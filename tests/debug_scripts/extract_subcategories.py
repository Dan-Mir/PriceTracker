"""
Estrae TUTTE le sottocategorie Castoro dall'HTML già renderizzato
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import platform

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
    time.sleep(8)
    
    print("\n📋 Estrazione sottocategorie dal menu...")
    
    # Trova TUTTE le sottocategorie (quelle con class="v-list-item__title subheaders")
    subcategories = driver.find_elements(By.CSS_SELECTOR, ".category2 .v-list-item__title.subheaders a")
    
    print(f"\n✅ Trovate {len(subcategories)} sottocategorie!\n")
    
    # Estrai e stampa tutte
    subcategory_data = []
    for sub in subcategories:
        name = sub.text.strip()
        url = sub.get_attribute('href')
        if url and name:
            subcategory_data.append((name, url))
    
    # Organizza per categoria principale
    current_main = None
    for name, url in subcategory_data:
        # Estrai categoria principale dall'URL
        parts = url.split('/category/')[1].split('/')
        main_cat = parts[0]
        
        if main_cat != current_main:
            current_main = main_cat
            print(f"\n📁 {main_cat.upper().replace('-', ' ')}")
        
        print(f"  ├─ {name:<35} → {url}")
    
    print(f"\n\n📊 TOTALE: {len(subcategory_data)} sottocategorie da scrapare")
    print(f"📈 Aumento previsto: da 89 a ~{len(subcategory_data)*6} prodotti")
    
    # Salva in file
    with open("castoro_subcategories.txt", "w") as f:
        for name, url in subcategory_data:
            f.write(f"{name}\t{url}\n")
    
    print("\n💾 Lista salvata in: castoro_subcategories.txt")
    
finally:
    driver.quit()
