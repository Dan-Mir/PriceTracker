# 🚀 Quick Start - Guida Rapida Post-Refactoring

## ⚡ Setup Veloce (5 minuti)

### 1. Installazione Dipendenze

```bash
cd /home/danym/Desktop/supermarket_parser

# Attiva virtual environment
source .venv/bin/activate

# Installa dipendenze (se non già fatto)
pip install -r requirements.txt
```

### 2. Configurazione Email

Crea/modifica il file `.env` nella root del progetto:

```bash
# File: .env
EUROSPIN_EMAIL=tua_email@example.com
DEBUG=False
LOG_LEVEL=INFO
```

### 3. Primo Test

```bash
# Test che tutto funzioni
python test_refactoring.py

# Output atteso:
# ✅ Test passati: 6/6
# 🎉 TUTTI I TEST PASSATI!
```

### 4. Esecuzione Parser

```bash
cd src
python main.py
```

**Cosa succede:**
1. Si apre Chrome in headless mode
2. Carica cookie salvati (se presenti)
3. Se cookie validi → scraping automatico
4. Se cookie scaduti → chiede OTP via email
5. Salva nuovi cookie per prossime esecuzioni
6. Naviga categorie e salva prodotti con marca e unità misura
7. **NUOVO:** Log strutturati in `logs/scraper.log`

---

## 🔍 Verifica Nuove Funzionalità

### Test Fuzzy Matching

```bash
cd src
python << EOF
from normalizer import fuzzy_match

# Test 1: Prodotti simili
print("Test 1:", fuzzy_match("Latte Intero 1L", "LATTE INTERO 1000ML"))
# Output: True (sono lo stesso prodotto)

# Test 2: Prodotti diversi
print("Test 2:", fuzzy_match("Coca Cola", "Pepsi"))
# Output: False (prodotti diversi)

# Test 3: Varianti ortografiche
print("Test 3:", fuzzy_match("Olio Extravergine", "OLIO EXTRA VERGINE"))
# Output: True (stesso prodotto)
EOF
```

### Test Estrazione Unità Misura

```bash
cd src
python << EOF
from normalizer import extract_unit

prodotti = [
    "Pasta Barilla 500g",
    "Latte Parmalat 1L",
    "Acqua Minerale 6x1,5L",
    "Biscotti 400 gr",
    "Yogurt 125ml x 4"
]

for p in prodotti:
    unit = extract_unit(p)
    print(f"{p:<30} → {unit}")
EOF
```

**Output atteso:**
```
Pasta Barilla 500g             → 500g
Latte Parmalat 1L              → 1l
Acqua Minerale 6x1,5L          → 1,5l
Biscotti 400 gr                → 400 gr
Yogurt 125ml x 4               → 125ml
```

### Visualizza Log in Tempo Reale

Durante lo scraping, in un altro terminale:

```bash
cd /home/danym/Desktop/supermarket_parser
tail -f logs/scraper.log
```

**Output esempio:**
```
2026-01-25 15:30:12 - parser - INFO - === INIZIO LOGIN ===
2026-01-25 15:30:15 - parser - INFO - Sessione ripristinata (cookie + storage)
2026-01-25 15:30:18 - parser - INFO - Sessione valida - 45 prezzi visibili
2026-01-25 15:30:18 - parser - INFO - SESSIONE RIPRISTINATA! Salto il login
2026-01-25 15:30:21 - parser - INFO - === INIZIO CRAWLER ===
2026-01-25 15:30:24 - parser - INFO - Coda iniziale: 12 categorie
2026-01-25 15:30:27 - parser - INFO - [1/60] Visito categoria: Frutta e Verdura
2026-01-25 15:30:35 - parser - INFO - Trovati 24 prodotti in categoria
...
```

---

## 📊 Controllo Database

### Visualizza Prodotti Salvati

```bash
cd src
python show_db.py
```

### Visualizza Offerte

```bash
cd src
python show_offers.py
```

**Output esempio:**
```
🎯 === PRODOTTI IN OFFERTA === 🎯

📊 Statistiche Database:
   • Prodotti totali: 342
   • Supermercati: 1
   • Rilevazioni prezzi: 487
   • Prodotti in offerta: 28

🔥 Top 28 Offerte (sconto >= 5%):

PRODOTTO                               MARCA          PRIMA     ORA       SCONTO    SUPERMERCATO
====================================================================================================
Pasta Barilla Spaghetti 500g           BARILLA        €1.99     €1.29     35.2%     Eurospin
Olio Extravergine 1L                   CARAPELLI      €8.99     €5.99     33.4%     Eurospin
Latte Intero 1L                        PARMALAT       €1.49     €1.09     26.8%     Eurospin
...
```

---

## 🎛️ Personalizzazione Configurazione

### Modifica Delay e Timeout

Edita `src/config.py`:

```python
# Per scraping più veloce (più rischio ban)
PAGE_LOAD_DELAY = 3       # default: 5
REQUEST_DELAY_MIN = 1     # default: 2
REQUEST_DELAY_MAX = 3     # default: 5

# Per scraping più lento (più sicuro)
PAGE_LOAD_DELAY = 8
REQUEST_DELAY_MIN = 5
REQUEST_DELAY_MAX = 10
```

### Modifica Soglia Fuzzy Matching

```python
# Più permissivo (cattura più match)
FUZZY_MATCH_THRESHOLD = 70  # default: 80

# Più restrittivo (solo match certi)
FUZZY_MATCH_THRESHOLD = 90
```

### Abilita Debug Logging

```python
LOG_LEVEL = "DEBUG"  # Mostra tutto (molto verbose)
```

Oppure nel file `.env`:
```
LOG_LEVEL=DEBUG
```

---

## 🛠️ Comandi Utili

### Pulizia Database

```bash
cd src
python clean_db.py
```

**⚠️ ATTENZIONE:** Elimina tutti i dati! Fai backup prima.

### Backup Database

```bash
# Backup manuale
cp src/prezzi.db backup_$(date +%Y%m%d_%H%M%S).db

# Backup con compressione
tar -czf backup_db_$(date +%Y%m%d).tar.gz src/prezzi.db logs/
```

### Filtra Log

```bash
# Solo errori
grep ERROR logs/scraper.log

# Solo warning ed errori
grep -E "WARNING|ERROR" logs/scraper.log

# Ultimi 50 log
tail -n 50 logs/scraper.log

# Log di oggi
grep "$(date +%Y-%m-%d)" logs/scraper.log
```

### Statistiche Database

```bash
cd src
python << EOF
from db import PriceDatabase

db = PriceDatabase()
stats = db.get_stats()

print("📊 Statistiche Database:")
for key, value in stats.items():
    print(f"   • {key}: {value}")

db.close()
EOF
```

---

## 🔄 Automazione (Cron/Scheduler)

### Setup Cron (Linux/Raspberry Pi)

```bash
crontab -e

# Aggiungi questa linea per esecuzione settimanale (domenica alle 3:00)
0 3 * * 0 cd /home/danym/Desktop/supermarket_parser/src && /home/danym/Desktop/supermarket_parser/.venv/bin/python main.py >> /home/danym/Desktop/supermarket_parser/logs/cron.log 2>&1
```

### Setup Scheduler Python

```bash
cd src
python scheduler.py
```

Il processo rimane in esecuzione e lancia scraping agli orari configurati.

### Verifica Ultima Esecuzione

```bash
# Controlla log
tail -20 logs/scraper.log

# Controlla timestamp DB
cd src
python << EOF
from db import PriceDatabase
db = PriceDatabase()
cursor = db.conn.execute("SELECT MAX(ultimo_scraping) FROM supermercati WHERE nome='Eurospin'")
print("Ultimo scraping:", cursor.fetchone()[0])
db.close()
EOF
```

---

## 🐛 Troubleshooting

### Problema: Moduli non trovati

```bash
# Assicurati di essere nel virtualenv
source .venv/bin/activate

# Reinstalla dipendenze
pip install -r requirements.txt
```

### Problema: Cookie scaduti continuamente

```bash
# Elimina cookie vecchi
rm src/cookies.pkl

# Riavvia parser (chiederà nuovo OTP)
cd src
python main.py
```

### Problema: ChromeDriver non trovato

```bash
# Reinstalla webdriver-manager
pip install --upgrade webdriver-manager

# Oppure installa ChromeDriver manualmente
# Su Raspberry Pi:
sudo apt install chromium-chromedriver
```

### Problema: Log troppo verbosi

Modifica `src/config.py`:
```python
LOG_LEVEL = "WARNING"  # Solo warning ed errori
```

### Problema: Database corrotto

```bash
# Ripristina da backup
cp backup_*.db src/prezzi.db

# Oppure ricrea da zero
rm src/prezzi.db
cd src
python main.py
```

---

## 📚 Risorse Aggiuntive

- **Dettagli Refactoring:** [REFACTORING_FASE1.md](REFACTORING_FASE1.md)
- **Riepilogo:** [SUMMARY_FASE1.md](SUMMARY_FASE1.md)
- **Documentazione Completa:** [README.md](README.md)
- **Automazione:** [AUTOMAZIONE.md](AUTOMAZIONE.md)
- **Multi-Supermercato:** [SUPERMERCATI.md](SUPERMERCATI.md)

---

## 🎯 Prossimi Passi

1. **Esegui il parser** almeno una volta per popolare il database
2. **Configura automazione** (cron o scheduler) per aggiornamenti settimanali
3. **Monitora log** per eventuali errori
4. **Aspetta Fase 2** per Shopping Optimizer e LLM Integration!

---

## ❓ Hai Domande?

Controlla la FAQ in [SUMMARY_FASE1.md](SUMMARY_FASE1.md) oppure leggi i log dettagliati per debugging.

**Buon scraping! 🛒🚀**
