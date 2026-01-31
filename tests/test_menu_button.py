"""
Test rapido per cliccare il pulsante menu con CSS selector
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    
    # Rimuovi cookie banner
    driver.execute_script("""
        var banner = document.getElementById('iubenda-cs-banner');
        if (banner) banner.remove();
    """)
    
    # Attendi e clicca pulsante menu con CSS selector
    print("\n🔍 Attesa pulsante menu...")
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.drawer-btn")))
    
    print("✓ Pulsante trovato, click con JavaScript...")
    driver.execute_script("arguments[0].click();", button)
    time.sleep(5)
    
    # Verifica se menu è aperto
    menu = driver.find_element(By.CSS_SELECTOR, "nav.drawer-left")
    transform = menu.value_of_css_property("transform")
    print(f"\nMenu transform: {transform}")
    
    if "translateX(-100%)" not in transform and "translateX(0)" in transform:
        print("✅ Menu aperto correttamente!")
        
        # Estrai categorie principali
        categories = driver.find_elements(By.CSS_SELECTOR, ".all-products .v-list-item__title a")
        print(f"\n📁 Categorie principali trovate: {len(categories)}")
        
        for cat in categories[:5]:
            print(f"  • {cat.text}")
    else:
        print("❌ Menu non si è aperto")
    
    # Screenshot
    driver.save_screenshot("menu_opened.png")
    print("\nScreenshot: menu_opened.png")
    
finally:
    driver.quit()
