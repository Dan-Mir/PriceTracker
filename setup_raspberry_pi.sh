#!/bin/bash

# Script di installazione per Raspberry Pi (ARM64/aarch64)

echo "🍓 Setup Raspberry Pi - Supermarket Parser"
echo "=========================================="

echo ""
echo "🔄 1. Aggiornamento sistema..."
sudo apt-get update -y

echo ""
echo "🌍 2. Installazione Chromium Browser..."
sudo apt-get install -y chromium chromium-driver

echo ""
echo "🔗 3. Creazione link simbolico ChromeDriver..."
# Trova il percorso di chromedriver
if [ -f /usr/lib/chromium/chromedriver ]; then
    sudo ln -sf /usr/lib/chromium/chromedriver /usr/bin/chromedriver
    echo "   ✅ Link creato: /usr/lib/chromium/chromedriver -> /usr/bin/chromedriver"
elif [ -f /usr/bin/chromedriver ]; then
    echo "   ✅ ChromeDriver già presente in /usr/bin"
else
    CHROMEDRIVER_PATH=$(which chromedriver 2>/dev/null)
    if [ -n "$CHROMEDRIVER_PATH" ]; then
        sudo ln -sf "$CHROMEDRIVER_PATH" /usr/bin/chromedriver
        echo "   ✅ Link creato: $CHROMEDRIVER_PATH -> /usr/bin/chromedriver"
    else
        echo "   ⚠️  ChromeDriver non trovato"
    fi
fi

echo ""
echo "🔍 4. Verifica installazione..."
echo "   Chromium: $(chromium --version 2>/dev/null || echo 'Non trovato')"
echo "   ChromeDriver: $(chromedriver --version 2>/dev/null || echo 'Non trovato')"

echo ""
echo "🐍 5. Setup Python Virtual Environment..."
if [ ! -d ".venv" ]; then
    echo "   Creazione virtual environment..."
    python3 -m venv .venv
fi

echo "   Attivazione virtual environment..."
source .venv/bin/activate

echo ""
echo "📦 6. Installazione dipendenze Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "📝 7. Setup file .env..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Configurazione Eurospin
EUROSPIN_EMAIL=tua_email@example.com

# Debug
DEBUG=False
LOG_LEVEL=INFO

# Screenshot (opzionale)
SAVE_SCREENSHOTS=False
EOF
    echo "   ✅ File .env creato - MODIFICA CON LA TUA EMAIL!"
    echo "   Usa: nano .env"
else
    echo "   ℹ️  File .env già esistente"
fi

echo ""
echo "🧪 8. Test configurazione..."
cd src
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Usa chromium su Raspberry Pi
    options.binary_location = '/usr/bin/chromium'
    
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://www.google.com')
    print('   ✅ Selenium funziona correttamente!')
    driver.quit()
except Exception as e:
    print(f'   ❌ Errore test Selenium: {e}')
    sys.exit(1)
"
TEST_RESULT=$?
cd ..

echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ ========================================"
    echo "✅ Setup completato con successo!"
    echo "✅ ========================================"
    echo ""
    echo "📋 Prossimi passi:"
    echo "   1. Modifica .env con la tua email:"
    echo "      nano .env"
    echo ""
    echo "   2. Esegui il parser:"
    echo "      cd src"
    echo "      python main.py"
    echo ""
    echo "   3. Controlla i log:"
    echo "      tail -f logs/scraper.log"
else
    echo "❌ ========================================"
    echo "❌ Setup completato con ERRORI"
    echo "❌ ========================================"
    echo ""
    echo "Controlla i messaggi di errore sopra."
fi
