from parser import EurospinParser
import time
import threading
import os
import shutil

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
    
    email = "danymirto8@gmail.com"
    bot = EurospinParser()
    
    # Avviamo il thread di registrazione
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
        recorder_thread.join()
        bot.close()
        
        # Creiamo lo ZIP
        print("📦 Creazione archivio ZIP...")
        shutil.make_archive('debug_video', 'zip', SCREENSHOT_DIR)
        print(f"✅ FATTO! Scarica il file 'debug_video.zip' dalla cartella a sinistra.")

if __name__ == "__main__":
    run_debug_session()