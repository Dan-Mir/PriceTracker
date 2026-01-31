"""Debug: verifica categorie e prodotti Castoro"""
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
    # Carica homepage
    print("Caricamento homepage...")
    driver.get("https://www.castoro.shop")
    time.sleep(5)
    
    # Rimuovi cookie banner
    driver.execute_script("""
        var banner = document.getElementById('iubenda-cs-banner');
        if (banner) banner.remove();
    """)
    time.sleep(1)
    
    # Salva screenshot homepage
    driver.save_screenshot("castoro_debug_home.png")
    print("Screenshot homepage salvato: castoro_debug_home.png")
    
    # Prova diverse categorie URL
    test_urls = [
        "https://www.castoro.shop/category/pasta-riso-farine",
        "https://www.castoro.shop/category/pasta-riso-e-farine",
        "https://www.castoro.shop/category/latticini",
        "https://www.castoro.shop/category/salumi-e-formaggi",
        "https://www.castoro.shop/category/salumi-formaggi",
    ]
    
    for url in test_urls:
        print(f"\n🔍 Test: {url}")
        driver.get(url)
        time.sleep(3)
        
        # Cerca prodotti
        products = driver.find_elements(By.CSS_SELECTOR, ".product.product-card")
        print(f"   Prodotti trovati con '.product.product-card': {len(products)}")
        
        if len(products) > 0:
            print(f"   ✅ URL VALIDO!")
            driver.save_screenshot(f"castoro_category_{url.split('/')[-1]}.png")
            
            # Estrai primo prodotto
            if products:
                p = products[0]
                try:
                    nome = p.find_element(By.CSS_SELECTOR, ".product-name").text
                    prezzo = p.find_element(By.CSS_SELECTOR, ".product-price").text
                    print(f"   Esempio: {nome} - {prezzo}")
                except:
                    print("   ⚠️  Errore estrazione dati")
        else:
            print(f"   ❌ Nessun prodotto")
    
    # Cerca tutti i link a categorie
    print("\n📋 Links presenti nella homepage:")
    links = driver.find_elements(By.TAG_NAME, "a")
    category_links = [l.get_attribute('href') for l in links if l.get_attribute('href') and 'category' in l.get_attribute('href')]
    
    unique_categories = list(set(category_links))
    for cat in sorted(unique_categories)[:20]:
        print(f"   {cat}")

finally:
    driver.quit()
