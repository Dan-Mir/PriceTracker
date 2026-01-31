"""
Apre il menu Castoro con trigger Vue.js diretto
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import platform

options = webdriver.ChromeOptions()
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
    
    print("\n📱 Apertura menu con trigger Vue...")
    
    # Apri il drawer modificando lo style direttamente
    result = driver.execute_script("""
        var drawer = document.querySelector('nav.drawer-left');
        if (drawer) {
            drawer.style.transform = 'translateX(0)';
            drawer.classList.remove('v-navigation-drawer--close');
            drawer.classList.add('v-navigation-drawer--open');
            return 'Menu aperto via style';
        }
        return 'Menu non trovato';
    """)
    
    print(f"Risultato: {result}")
    time.sleep(2)
    
    # Screenshot
    driver.save_screenshot("menu_forced_open.png")
    print("Screenshot: menu_forced_open.png")
    
    # Ora estrai sottocategorie
    print("\n📋 Estrazione sottocategorie...")
    subcats = driver.find_elements(By.CSS_SELECTOR, ".category2 .v-list-item__title.subheaders a")
    print(f"Trovate: {len(subcats)} sottocategorie")
    
    for sub in subcats[:10]:
        print(f"  • {sub.text} → {sub.get_attribute('href')}")
    
finally:
    driver.quit()
