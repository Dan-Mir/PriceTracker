"""
Scheduler automatico per eseguire periodicamente lo scraping
Può essere eseguito come servizio Windows o tramite Task Scheduler
"""
import schedule
import time
import subprocess
import sys
import os
from datetime import datetime
import logging

# Configurazione logging
log_file = os.path.join(os.path.dirname(__file__), "scheduler.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def run_scraper():
    """Esegue lo script di scraping"""
    logging.info("=" * 70)
    logging.info("INIZIO ESECUZIONE SCRAPING PROGRAMMATO")
    logging.info("=" * 70)
    
    try:
        # Path assoluto dello script main.py
        script_path = os.path.join(os.path.dirname(__file__), "main.py")
        
        # Esegui lo script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=3600  # Timeout 1 ora
        )
        
        if result.returncode == 0:
            logging.info("✅ Scraping completato con successo")
            logging.info(f"Output:\n{result.stdout}")
        else:
            logging.error(f"❌ Scraping fallito con codice {result.returncode}")
            logging.error(f"Errore:\n{result.stderr}")
            
    except subprocess.TimeoutExpired:
        logging.error("⏰ Timeout - Scraping interrotto dopo 1 ora")
    except Exception as e:
        logging.error(f"❌ Errore durante l'esecuzione: {e}")
    
    logging.info("=" * 70)
    logging.info(f"Prossima esecuzione programmata alle: {schedule.idle_seconds() / 3600:.1f} ore")
    logging.info("=" * 70 + "\n")

def main():
    """Main scheduler loop"""
    logging.info("🕐 SCHEDULER AVVIATO")
    logging.info("=" * 70)
    
    # ===== CONFIGURAZIONE PROGRAMMAZIONE =====
    # Opzione 1: Esegui ogni giorno alle 03:00 (orario notturno)
    schedule.every().day.at("03:00").do(run_scraper)
    
    # Opzione 2: Esegui ogni 12 ore
    # schedule.every(12).hours.do(run_scraper)
    
    # Opzione 3: Esegui ogni settimana la domenica alle 02:00
    # schedule.every().sunday.at("02:00").do(run_scraper)
    
    # Opzione 4: Esegui ogni 2 giorni
    # schedule.every(2).days.do(run_scraper)
    # ==========================================
    
    logging.info("📅 Programmazione configurata:")
    for job in schedule.get_jobs():
        logging.info(f"   • {job}")
    
    # Esecuzione immediata al primo avvio (opzionale)
    # Decommenta la riga seguente per eseguire subito al primo avvio
    # run_scraper()
    
    # Loop infinito
    logging.info("\n⏰ In attesa della prossima esecuzione programmata...")
    logging.info("   (Premi Ctrl+C per interrompere)\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Controlla ogni minuto
    except KeyboardInterrupt:
        logging.info("\n⏹️ Scheduler interrotto dall'utente")
        sys.exit(0)

if __name__ == "__main__":
    main()
