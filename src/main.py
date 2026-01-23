from parser import EurospinParser
import time
import threading
import os
import shutil
import argparse
from dotenv import load_dotenv
load_dotenv()

# Configurazione Paparazzo
SCREENSHOT_DIR = "screenshots"
STOP_RECORDING = False

def paparazzi_cam(driver):
    """Funzione che gira in background e scatta foto a raffica"""
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
    
    # Pulizia vecchi screen
    for f in os.listdir(SCREENSHOT_DIR):
        os.remove(os.path.join(SCREENSHOT_DIR, f))

    count = 0
    print("🎥 REGISTRAZIONE AVVIATA (3 fps)...")
    
    while not STOP_RECORDING:
        try:
            # Nome file ordinato: snap_001.png, snap_002.png...
            filename = f"{SCREENSHOT_DIR}/snap_{count:04d}.png"
            driver.save_screenshot(filename)
            count += 1
            time.sleep(0.3) # Scatta ogni 0.3 secondi
        except:
            break

def run_debug_session():
    global STOP_RECORDING
    
    email = os.getenv("EUROSPIN_EMAIL")
    bot = EurospinParser()
    
    # Avviamo il thread di registrazione
    if args.screenshots:
        recorder_thread = threading.Thread(target=paparazzi_cam, args=(bot.driver,))
        recorder_thread.start()

    try:
        # Eseguiamo il login
        bot.login_interattivo(email)
        print("✅ Script terminato.")
        
    except Exception as e:
        print(f"❌ Errore nello script: {e}")
        
    finally:
        # Fermiamo la registrazione
        STOP_RECORDING = True
        if args.screenshots:
            recorder_thread.join()
            print("🎥 REGISTRAZIONE TERMINATA.")
            # Creiamo lo ZIP
            print("📦 Creazione archivio ZIP...")
            shutil.make_archive('debug_video', 'zip', SCREENSHOT_DIR)
            print(f"✅ FATTO! Scarica il file 'debug_video.zip' dalla cartella a sinistra.")
        bot.close()
        
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Esegui una sessione di debug con registrazione dello schermo.")
    parser.add_argument('--screenshots', action='store_true', help="Abilita la registrazione dello schermo durante la sessione di debug.")
    args = parser.parse_args()
    run_debug_session()