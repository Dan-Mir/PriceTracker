# 🕐 Guida Rapida Cronjob - Scraper Settimanale

## ⚙️ Configurare il Cronjob

### Aprire l'editor crontab
```bash
EDITOR=nano crontab -e
```

### Aggiungere questa riga (lunedì alle 2:00 AM)
```bash
0 2 * * 1 /home/danym/Desktop/supermarket_parser/run_scraper.sh >> /home/danym/Desktop/supermarket_parser/logs/cron.log 2>&1
```

---

## 📋 Visualizzare i Cronjob Attivi

```bash
# Lista tutti i cronjob configurati
crontab -l

# Verifica che il servizio cron sia attivo
sudo systemctl status cron
```

---

## ✏️ Modificare il Cronjob

```bash
# Riapri l'editor
crontab -e

# Modifica l'orario o il giorno, poi salva
```

**Esempi orari:**
```bash
0 3 * * 0    # Domenica alle 3:00
0 2 * * 1    # Lunedì alle 2:00
0 4 * * 6    # Sabato alle 4:00
0 1 * * *    # Ogni giorno alle 1:00
```

Formato cron 
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Giorno della settimana (0-7, 0 e 7 = domenica)
│ │ │ └───── Mese (1-12)
│ │ └─────── Giorno del mese (1-31)
│ └───────── Ora (0-23)
└─────────── Minuto (0-59)
```

---

## ❌ Disabilitare/Rimuovere il Cronjob

### Opzione 1: Commentare (disabilita temporaneamente)
```bash
crontab -e

# Aggiungi # all'inizio della riga:
# 0 3 * * 0 /home/danym/Desktop/supermarket_parser/run_scraper.sh >> ...
```

### Opzione 2: Cancellare la riga (rimuove definitivamente)
```bash
crontab -e

# Elimina l'intera riga, poi salva
```

### Opzione 3: Cancellare TUTTI i cronjob
```bash
# ⚠️ ATTENZIONE: Rimuove TUTTI i cronjob dell'utente
crontab -r

# Conferma prima di procedere
crontab -l  # Vedi cosa verrà cancellato
crontab -r  # Poi cancella tutto
```

---

## 🧪 Testare Manualmente (senza aspettare il cron)

```bash
# Esegui lo script immediatamente
/home/danym/Desktop/supermarket_parser/run_scraper.sh

# Oppure in background
/home/danym/Desktop/supermarket_parser/run_scraper.sh &
```

---

## 📊 Monitorare le Esecuzioni

### Visualizzare log in tempo reale
```bash
# Log delle esecuzioni cron
tail -f ~/Desktop/supermarket_parser/logs/cron.log

# Log dello scraper (dettagliato)
tail -f ~/Desktop/supermarket_parser/logs/scraper.log
```

### Visualizzare ultimi 20 log
```bash
tail -20 ~/Desktop/supermarket_parser/logs/cron.log
tail -20 ~/Desktop/supermarket_parser/logs/scraper.log
```

### Cercare errori nei log
```bash
grep ERROR ~/Desktop/supermarket_parser/logs/scraper.log
grep -i error ~/Desktop/supermarket_parser/logs/cron.log
```

### Controllare l'ultima esecuzione
```bash
# Ultima riga del log cron
tail -1 ~/Desktop/supermarket_parser/logs/cron.log

# Ultimo timestamp nel database
cd ~/Desktop/supermarket_parser/src
python << EOF
from db import PriceDatabase
db = PriceDatabase()
cursor = db.conn.execute("SELECT MAX(ultimo_scraping) FROM supermercati WHERE nome='Eurospin'")
print("Ultimo scraping:", cursor.fetchone()[0])
db.close()
EOF
```

---

## 🔄 Riavviare il Servizio Cron

```bash
# Se il cron non funziona, riavvia il servizio
sudo systemctl restart cron

# Controlla lo status
sudo systemctl status cron
```

---

## 🚨 Troubleshooting

### Il cronjob non si esegue?

1. **Verifica che sia configurato:**
   ```bash
   crontab -l
   ```

2. **Verifica che cron sia attivo:**
   ```bash
   sudo systemctl status cron
   ```

3. **Controlla i permessi dello script:**
   ```bash
   ls -l ~/Desktop/supermarket_parser/run_scraper.sh
   # Deve mostrare: -rwxr-xr-x (eseguibile)
   
   # Se non eseguibile:
   chmod +x ~/Desktop/supermarket_parser/run_scraper.sh
   ```

4. **Controlla i log di sistema:**
   ```bash
   grep CRON /var/log/syslog | tail -20
   ```

5. **Testa lo script manualmente:**
   ```bash
   /home/danym/Desktop/supermarket_parser/run_scraper.sh
   ```

---

## 📅 Riferimento Rapido Cron

```
┌───────────── minuto (0-59)
│ ┌─────────── ora (0-23)
│ │ ┌───────── giorno del mese (1-31)
│ │ │ ┌─────── mese (1-12)
│ │ │ │ ┌───── giorno della settimana (0-7, 0 e 7 = domenica)
│ │ │ │ │
* * * * * comando da eseguire
```

**Esempi comuni:**
```bash
0 3 * * 0       # Ogni domenica alle 3:00
0 2 * * 1       # Ogni lunedì alle 2:00
0 0 * * *       # Ogni giorno a mezzanotte
0 */6 * * *     # Ogni 6 ore
0 0 1 * *       # Il primo giorno di ogni mese
0 0 * * 1-5     # Ogni giorno feriale (lun-ven)
```

---

## 💾 Backup Configurazione

```bash
# Salva la configurazione cron attuale
crontab -l > ~/crontab_backup_$(date +%Y%m%d).txt

# Ripristina da backup
crontab ~/crontab_backup_20260125.txt
```

---

## 🎯 Comandi Essenziali (Cheat Sheet)

```bash
# CONFIGURARE
crontab -e                                    # Modifica cronjob

# VISUALIZZARE
crontab -l                                    # Lista cronjob

# RIMUOVERE
crontab -e                                    # Cancella la riga, poi salva
crontab -r                                    # Rimuove TUTTI i cronjob

# TESTARE
/home/danym/Desktop/supermarket_parser/run_scraper.sh    # Test manuale

# MONITORARE
tail -f ~/Desktop/supermarket_parser/logs/cron.log       # Log esecuzioni
tail -f ~/Desktop/supermarket_parser/logs/scraper.log    # Log scraper

# STATUS
sudo systemctl status cron                    # Verifica servizio cron
```

---
