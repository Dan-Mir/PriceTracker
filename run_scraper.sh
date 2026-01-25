#!/bin/bash
# Script per eseguire lo scraper con logging automatico

# Directory del progetto
PROJECT_DIR="/home/danym/Desktop/supermarket_parser"

# Vai nella directory del progetto
cd "$PROJECT_DIR" || exit 1

# Attiva il virtual environment
source .venv/bin/activate

# Vai nella directory src
cd src || exit 1

# Esegui lo script principale
python main.py

# Log dell'esecuzione
echo "Scraping completato il $(date)" >> "$PROJECT_DIR/logs/cron.log"
