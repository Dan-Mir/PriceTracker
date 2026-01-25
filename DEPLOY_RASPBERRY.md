# 🚀 Deploy su Raspberry Pi - Guida Completa

## 📋 Pre-requisiti Raspberry Pi

- **OS**: Raspberry Pi OS (Debian-based)
- **RAM**: Minimo 1GB (2GB consigliato)
- **Python**: 3.8+
- **Connessione**: Internet stabile

---

## 🔧 Setup Iniziale

### 1. Update Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Installa Dipendenze Sistema

```bash
# Python e pip
sudo apt install python3 python3-pip python3-venv -y

# Chromium browser (per Selenium)
sudo apt install chromium-browser chromium-chromedriver -y

# Git (se non presente)
sudo apt install git -y
```

### 3. Verifica Installazione

```bash
python3 --version    # Deve essere >= 3.8
chromium-browser --version
chromedriver --version
```

---

## 📦 Clone Repository

```bash
cd ~
git clone https://github.com/TUO_USERNAME/supermarket_parser.git
cd supermarket_parser
```

---

## 🐍 Setup Python Environment

```bash
# Crea virtual environment
python3 -m venv .venv

# Attiva venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Installa dipendenze
pip install -r requirements.txt
```

---

## 🔐 Primo Login (Configurazione Sessione)

```bash
cd src
python main.py
```

**Procedura:**
1. Inserisci email: `tua_email@example.com`
2. Ricevi OTP via email
3. Inserisci codice OTP nel terminale
4. ✅ Sessione salvata in `cookies.pkl` (durata ~7 giorni)

**Verifica:**
```bash
# Re-esegui senza OTP (deve usare cookie salvati)
python main.py
# Se non chiede OTP → ✅ Sessione funzionante
```

---

## ⏰ Automazione con Cron

### Setup Cron Job

```bash
# Apri editor crontab
crontab -e

# Aggiungi esecuzione giornaliera ore 3:00
0 3 * * * /home/pi/supermarket_parser/.venv/bin/python /home/pi/supermarket_parser/src/main.py >> /home/pi/scraping.log 2>&1
```

**Spiegazione:**
- `0 3 * * *` → Ogni giorno alle 03:00
- `/home/pi/supermarket_parser/.venv/bin/python` → Python del venv
- `>> /home/pi/scraping.log 2>&1` → Log output e errori

### Verifica Cron

```bash
# Lista cron jobs
crontab -l

# Testa esecuzione manuale
/home/pi/supermarket_parser/.venv/bin/python /home/pi/supermarket_parser/src/main.py
```

---

## 📊 Monitoring

### Verifica Log

```bash
# Ultimi log
tail -f ~/scraping.log

# Ultime 50 righe
tail -50 ~/scraping.log

# Cerca errori
grep "ERROR\|❌" ~/scraping.log
```

### Verifica Database

```bash
cd ~/supermarket_parser/src
source ../.venv/bin/activate

# Statistiche
python show_db.py

# Offerte attive
python show_offers.py
```

### Check Spazio Disco

```bash
# Dimensione database
du -h ~/supermarket_parser/src/prezzi.db

# Spazio disponibile
df -h
```

---

## 🔄 Rinnovo Sessione (Ogni ~7 Giorni)

Quando i cookie scadono, lo script fallisce. Procedura rinnovo:

```bash
cd ~/supermarket_parser/src
source ../.venv/bin/activate

# Elimina cookie scaduti
rm cookies.pkl

# Nuovo login
python main.py
# → Inserisci email e nuovo OTP

# ✅ Sessione rinnovata per altri 7 giorni
```

**Opzione**: Crea reminder settimanale per rinnovo manuale.

---

## 🛠️ Troubleshooting

### Script non parte da cron

**Problema**: Cron usa ambiente diverso.

**Soluzione**: Usa path assoluti
```bash
# ❌ Sbagliato
python main.py

# ✅ Corretto
/home/pi/supermarket_parser/.venv/bin/python /home/pi/supermarket_parser/src/main.py
```

### Chromium non trovato

**Problema**: ChromeDriver non trova browser.

**Soluzione**:
```bash
# Verifica path
which chromium-browser

# Aggiorna parser.py se necessario
# Oppure crea symlink
sudo ln -s /usr/bin/chromium-browser /usr/bin/google-chrome
```

### Database bloccato

**Problema**: SQLite in uso da altro processo.

**Soluzione**:
```bash
# Trova processi Python
ps aux | grep python

# Kill processo se necessario
kill -9 <PID>
```

### Out of Memory (OOM)

**Problema**: Raspberry Pi con poca RAM.

**Soluzione**: Aggiungi swap
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Cambia CONF_SWAPSIZE=100 → CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 🚦 Performance Raspberry Pi

### Consumi Tipici

| Modello | RAM Usata | CPU Load | Durata Scraping |
|---------|-----------|----------|-----------------|
| Pi 3B+ | ~400MB | 40-60% | 15-20 min |
| Pi 4 (2GB) | ~350MB | 30-40% | 10-15 min |
| Pi 4 (4GB) | ~350MB | 25-35% | 10-12 min |
| Pi Zero 2W | ~500MB | 70-90% | 25-35 min |

### Ottimizzazioni

```python
# In parser.py, aumenta headless mode
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
```

---

## 📈 Backup Database

### Backup Automatico

```bash
# Crea script backup
nano ~/backup_db.sh
```

```bash
#!/bin/bash
# Backup database con timestamp
BACKUP_DIR="$HOME/db_backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
cp ~/supermarket_parser/src/prezzi.db "$BACKUP_DIR/prezzi_$DATE.db"
# Mantieni solo ultimi 30 backup
ls -t $BACKUP_DIR/prezzi_*.db | tail -n +31 | xargs rm -f
```

```bash
# Rendi eseguibile
chmod +x ~/backup_db.sh

# Aggiungi a cron (prima dello scraping)
crontab -e
# 0 2 * * * /home/pi/backup_db.sh
```

---

## 🌐 Accesso Remoto Database

### Opzione 1: Samba Share

```bash
sudo apt install samba -y
sudo nano /etc/samba/smb.conf
```

```ini
[supermarket_db]
path = /home/pi/supermarket_parser/src
read only = yes
browseable = yes
```

### Opzione 2: SQLite Web Viewer

```bash
pip install datasette

# Avvia server
datasette ~/supermarket_parser/src/prezzi.db --host 0.0.0.0 --port 8001
# Accedi da: http://raspberry-pi-ip:8001
```

---

## 🎯 Checklist Deploy

- [ ] Sistema aggiornato (`apt update && upgrade`)
- [ ] Python 3.8+ installato
- [ ] Chromium + ChromeDriver installati
- [ ] Repository clonata
- [ ] Virtual environment creato e attivato
- [ ] Dipendenze installate (`pip install -r requirements.txt`)
- [ ] Primo login OTP completato
- [ ] Sessione testata (secondo run senza OTP)
- [ ] Cron job configurato
- [ ] Log verificato (`tail -f ~/scraping.log`)
- [ ] Database popolato (`python show_db.py`)
- [ ] Backup automatico configurato (opzionale)

---

## 📞 Supporto

**Issues**: [GitHub Issues](https://github.com/TUO_USERNAME/supermarket_parser/issues)  
**Docs**: Vedi `README.md`, `AUTOMAZIONE.md`

---

**Pronto per il deploy! 🚀**
