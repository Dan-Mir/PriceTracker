#!/bin/bash
# Script per eseguire lo scraping periodico di tutti i supermercati
# Include Eurospin e Castoro Shop con paginazione completa
# 
# Aggiungi al cron per esecuzione automatica giornaliera:
# 0 2 * * * /home/danym/Desktop/supermarket_parser/run_scraping.sh
#
# Oppure settimanale (domenica alle 2:00):
# 0 2 * * 0 /home/danym/Desktop/supermarket_parser/run_scraping.sh

cd /home/danym/Desktop/supermarket_parser

# Crea cartella logs se non esiste
mkdir -p logs

# Attiva virtual environment
source .venv/bin/activate

# Nome file log con data
LOG_FILE="logs/scraping_$(date +\%Y\%m\%d_\%H\%M).log"

# Esegui scraping di tutti i supermercati
echo "========================================" | tee -a "$LOG_FILE"
echo "$(date): Inizio scraping supermercati" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

python src/scrape_all.py --all >> "$LOG_FILE" 2>&1

# Verifica risultato
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "$(date): ✅ Scraping completato con successo" | tee -a "$LOG_FILE"
    
    # Mostra statistiche database
    echo "" | tee -a "$LOG_FILE"
    echo "📊 Statistiche database:" | tee -a "$LOG_FILE"
    python -c "from src.db import PriceDatabase; db = PriceDatabase(); stats = db.get_stats(); print(f'Prodotti: {stats[\"totale_prodotti\"]}, Supermercati: {stats[\"totale_supermercati\"]}, Rilevazioni: {stats[\"totale_rilevazioni\"]}')" | tee -a "$LOG_FILE"
else
    echo "" | tee -a "$LOG_FILE"
    echo "$(date): ❌ Errore durante scraping (exit code: $EXIT_CODE)" | tee -a "$LOG_FILE" >&2
fi

echo "========================================" | tee -a "$LOG_FILE"
echo "Log salvato in: $LOG_FILE"
