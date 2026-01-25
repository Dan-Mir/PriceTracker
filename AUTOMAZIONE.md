# 🕐 Guida Automazione Scraping

Questa guida spiega come configurare l'esecuzione automatica periodica dello scraping.

---

## 📋 Metodi Disponibili

### 1. **Python Scheduler (Consigliato per sviluppo)**
Script Python che rimane in esecuzione e lancia lo scraping a orari programmati.

### 2. **Windows Task Scheduler (Consigliato per produzione)**
Utilizza l'Utilità di pianificazione di Windows per eseguire lo script a intervalli regolari.

### 3. **Docker + Cron (Avanzato)**
Containerizzazione con cron job per deployment su server Linux/Raspberry Pi.

---

## 🐍 Metodo 1: Python Scheduler

### Installazione dipendenza
```bash
pip install schedule
```

### Configurazione
Modifica `src/scheduler.py` per impostare la frequenza:

```python
# Opzione 1: Ogni giorno alle 03:00
schedule.every().day.at("03:00").do(run_scraper)

# Opzione 2: Ogni 12 ore
schedule.every(12).hours.do(run_scraper)

# Opzione 3: Ogni domenica alle 02:00
schedule.every().sunday.at("02:00").do(run_scraper)

# Opzione 4: Ogni 2 giorni
schedule.every(2).days.do(run_scraper)
```

### Esecuzione
```bash
cd src
python scheduler.py
```

Lo script rimarrà in esecuzione e lancerà automaticamente lo scraping agli orari programmati.

**⚠️ Nota**: Il terminale/prompt deve rimanere aperto. Per esecuzione persistente usa il Metodo 2.

### Log
I log sono salvati in `src/scheduler.log`

---

## 🪟 Metodo 2: Windows Task Scheduler (RACCOMANDATO)

### Setup Manuale

1. **Apri Utilità di pianificazione**
   - Premi `Win + R`
   - Digita `taskschd.msc`
   - Invio

2. **Crea Nuova Attività**
   - Click su "Crea attività..." (non "Crea attività di base")

3. **Scheda Generale**
   - Nome: `Eurospin Price Scraper`
   - Descrizione: `Scraping automatico prezzi Eurospin`
   - ☑️ Esegui indipendentemente dalla connessione degli utenti
   - ☑️ Esegui con i privilegi più elevati (se necessario)

4. **Scheda Trigger**
   - Click "Nuovo..."
   - **Per esecuzione giornaliera:**
     - Inizio attività: `In base a una pianificazione`
     - Impostazioni: `Giornaliera`
     - Ora: `03:00:00` (orario notturno consigliato)
     - Ricorrenza: ogni `1` giorno
   - **Per esecuzione settimanale:**
     - Impostazioni: `Settimanale`
     - Seleziona giorni (es. Domenica)
   - ☑️ Abilitato
   - OK

5. **Scheda Azioni**
   - Click "Nuovo..."
   - Azione: `Avvio programma`
   - Programma/Script: 
     ```
     C:\Users\danym\Desktop\Python projects\supermarket_parser\run_scraping.bat
     ```
   - Oppure (esecuzione diretta Python):
     - Programma: `C:\Users\danym\Desktop\Python projects\supermarket_parser\.venv\Scripts\python.exe`
     - Argomenti: `main.py`
     - Inizio da: `C:\Users\danym\Desktop\Python projects\supermarket_parser\src`
   - OK

6. **Scheda Condizioni**
   - ☑️ Avvia l'attività solo se il computer è collegato alla rete elettrica (se laptop)
   - ☑️ Riattiva il computer per eseguire l'attività (opzionale)

7. **Scheda Impostazioni**
   - ☑️ Consenti esecuzione dell'attività su richiesta
   - ☑️ Esegui l'attività appena possibile dopo la mancata esecuzione pianificata
   - Se l'attività è già in esecuzione: `Non avviare una nuova istanza`
   - ☑️ Se l'attività non viene completata entro: `2 ore` → `Arresta attività esistente`

8. **Salva**
   - OK
   - Inserisci password utente se richiesta

### Test Manuale
- Tasto destro sull'attività → "Esegui"
- Controlla il log in `scraping.log`

### Setup Automatico (PowerShell)

```powershell
# Crea attività programmata giornaliera alle 03:00
$action = New-ScheduledTaskAction -Execute "C:\Users\danym\Desktop\Python projects\supermarket_parser\run_scraping.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -TaskName "Eurospin Price Scraper" -Description "Scraping automatico prezzi supermercato"
```

---

## 📊 Monitoraggio e Log

### File di Log
- **Scheduler Python**: `src/scheduler.log`
- **Batch Windows**: `scraping.log` (root del progetto)
- **Database**: Controlla timestamp aggiornamenti in `prezzi.db`

### Verifica Ultima Esecuzione
```python
from db import PriceDatabase
db = PriceDatabase()
stats = db.get_stats()
print(stats)
db.close()
```

### Query Supermercati
```python
from db import PriceDatabase
db = PriceDatabase()
conn = db.conn
cursor = conn.execute("SELECT nome, ultimo_scraping FROM supermercati")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")
db.close()
```

---

## ⚙️ Configurazione Avanzata

### Email Notifiche (Opzionale)
Aggiungi al `scheduler.py` per ricevere email al completamento:

```python
import smtplib
from email.message import EmailMessage

def send_email_notification(status, message):
    msg = EmailMessage()
    msg['Subject'] = f'Scraping Eurospin - {status}'
    msg['From'] = 'tua@email.com'
    msg['To'] = 'destinatario@email.com'
    msg.set_content(message)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('tua@email.com', 'password_app')
        smtp.send_message(msg)

# Chiama dopo run_scraper()
send_email_notification("Successo", "Scraping completato")
```

### Telegram Bot (Opzionale)
```python
import requests

def send_telegram_message(message):
    token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})
```

---

## 🔧 Troubleshooting

### Lo script non parte da Task Scheduler
- Verifica path assoluti (non relativi)
- Controlla permessi utente
- Esegui come amministratore se necessario
- Verifica che il virtual environment sia attivato nel batch

### Cookie scaduti ogni volta
- Verifica che `cookies.pkl` venga salvato correttamente
- Controlla permessi scrittura nella cartella
- I cookie Eurospin scadono dopo ~7 giorni: normale richiedere OTP settimanalmente

### Errori di rete
- Verifica connessione internet
- Aggiungi retry logic in `parser.py`
- Aumenta timeout in `scheduler.py`

### Database locked
- Un solo script alla volta
- Chiudi connessioni DB correttamente
- Aggiungi lock file per evitare esecuzioni concorrenti

---

## 📅 Best Practices

1. **Frequenza Scraping**
   - ✅ Giornaliero: sufficiente per tracking offerte
   - ✅ Ogni 2-3 giorni: per risparmiare risorse
   - ❌ Ogni ora: troppo frequente, rischio ban

2. **Orario Consigliato**
   - 🌙 Notte (02:00 - 05:00): meno carico server
   - ⚠️ Evita ore di punta (18:00 - 21:00)

3. **Manutenzione**
   - Controlla log settimanalmente
   - Pulisci vecchi record DB mensile
   - Aggiorna parser se il sito cambia

4. **Backup**
   - Backup database settimanale
   - Salva cookie in cloud (opzionale)

---

## 📝 Esempio Completo Windows Task Scheduler

**File XML per importazione rapida**:
Salva come `eurospin_task.xml` e importa in Task Scheduler.

```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2">
  <RegistrationInfo>
    <Description>Scraping automatico prezzi Eurospin</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-24T03:00:00</StartBoundary>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal>
      <UserId>TUO_USERNAME</UserId>
      <LogonType>Password</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
  </Settings>
  <Actions>
    <Exec>
      <Command>C:\Users\danym\Desktop\Python projects\supermarket_parser\run_scraping.bat</Command>
    </Exec>
  </Actions>
</Task>
```

**Importa con**: Task Scheduler → Importa attività... → Seleziona il file XML

---

**Ultimo aggiornamento**: Gennaio 2026
