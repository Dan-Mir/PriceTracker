#!/bin/bash

# Script di installazione per Google Colab (Ambiente Linux x64)

echo "🔄 1. Pulizia e aggiornamento..."
sudo apt-get update -y
sudo apt-get install -y wget curl unzip

echo "🌍 2. Installazione Chrome Stable..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb
apt-get install -f -y

echo "🔧 3. Setup ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | awk '{print $3}')
echo "   Versione Chrome rilevata: $CHROME_VERSION"
wget -N "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip"
unzip -o chromedriver-linux64.zip
mv -f chromedriver-linux64/chromedriver /usr/bin/chromedriver
chown root:root /usr/bin/chromedriver
chmod +x /usr/bin/chromedriver

echo "🐍 4. Installazione Librerie Python..."
pip install -r requirements.txt

echo "✅ Setup completato!"