# 🛒 Supermarket Price Scraper

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-green.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema automatico di scraping multi-supermercato per confronto prezzi e analisi. Supporta Eurospin e Castoro Shop con database centralizzato e assistente LLM integrato.

---

## 📊 Panoramica

| Supermercato | Prodotti | Tecnologia | Status |
|-------------|----------|------------|--------|
| **Eurospin** | ~350 | Shadow DOM + Session | ✅ Attivo |
| **Castoro Shop** | 1000+ | Vue.js SPA + Paginazione (109 categorie) | ✅ Attivo |
| **TOTALE** | **~1350+** | SQLite Database | 🟢 Online |

**Funzionalità Principali:**
- 🔄 Scraping automatico con paginazione intelligente
- 🤖 Assistente LLM (Ollama/Gemma) per ricerca prodotti
- 📈 Database storico prezzi con tracking temporale
- 🎯 Confronto prezzi multi-store
- ⏰ Automazione completa via cron job

---

## 🚀 Quick Start

### Installazione

```bash
# Clone repository
git clone <repo-url>
cd supermarket_parser

# Setup ambiente virtuale
python3 -m venv .venv
source .venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Configura email Eurospin
echo "EUROSPIN_EMAIL=tua.email@esempio.com" > .env
```

### Primo Utilizzo

```bash
# 1. Esegui scraping
./run_scraping.sh

# 2. Visualizza database
python src/show_db.py

# 3. Cerca offerte
python src/show_offers.py "pasta"

# 4. Assistente LLM (richiede Ollama)
python demo_llm.py
```

---

## ⚙️ Automazione

### Setup Cron Job

Configurazione per esecuzione settimanale automatica:

```bash
# Modifica crontab
crontab -e

# Aggiungi (esecuzione domenica ore 2:00)
0 2 * * 0 /home/danym/Desktop/supermarket_parser/run_scraping.sh
```

### Monitoring Logs

```bash
# Visualizza log in tempo reale
tail -f logs/scraping_$(date +%Y%m%d)_*.log

# Statistiche database
python src/show_db.py

# Verifica errori
grep -i error logs/*.log | tail -20
```

---

## 📁 Struttura Progetto

```
supermarket_parser/
├── run_scraping.sh              # ⭐ Script automazione principale
├── src/
│   ├── scrape_all.py            # Orchestrator scraping multi-store
│   ├── parser.py                # Parser Eurospin (Shadow DOM)
│   ├── castoro_parser.py        # Parser Castoro (109 categorie + paginazione)
│   ├── castoro_all_urls.py      # Lista URL categorie Castoro
│   ├── db.py                    # Database SQLite manager
│   ├── llm_interface.py         # Interfaccia LLM per ricerca intelligente
│   ├── config.py                # Configurazione centralizzata
│   ├── normalizer.py            # Normalizzazione prodotti/fuzzy matching
│   ├── utils.py                 # Utilities (retry, rate limiting)
│   ├── show_db.py               # Visualizza contenuto database
│   └── show_offers.py           # Cerca migliori offerte
├── tests/                       # Test e script di debug
│   ├── debug_scripts/           # Script esplorazione/debug
│   └── run_tests.py             # Esecuzione test suite
├── logs/                        # Log di scraping
└── README.md                    # Questa documentazione
```

---

## 🔧 Configurazione

### Variabili Ambiente (.env)

```env
# Email per login Eurospin (obbligatorio)
EUROSPIN_EMAIL=tua.email@esempio.com

# LLM (opzionale - richiede Ollama installato)
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=functiongemma:2b
```

### Parametri Scraping (src/config.py)

```python
# Timing
CATEGORY_DELAY = 5              # Delay tra categorie (secondi)
PAGE_LOAD_DELAY = 8             # Attesa caricamento pagina
RETRY_DELAY = 3                 # Delay tra retry

# Browser
HEADLESS = True                 # Browser senza interfaccia grafica
WINDOW_SIZE = (1920, 1080)      # Risoluzione finestra

# Paginazione
MAX_PAGINATION_PAGES = 20       # Massimo pagine per categoria
```

---

## 🤖 Assistente LLM

Sistema di ricerca intelligente prodotti usando linguaggio naturale.

### Setup Ollama

```bash
# Installa Ollama (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Scarica modello (2GB)
ollama pull functiongemma:2b

# Verifica installazione
ollama list
```

### Utilizzo

```python
from src.llm_interface import LLMShoppingAssistant

assistant = LLMShoppingAssistant()

# Ricerca singolo prodotto
result = assistant.chat("Qual è il miglior prezzo per pasta barilla?")
print(result)

# Query complessa
result = assistant.chat("Voglio fare una carbonara, cosa mi serve?")
```

**Capacità:**
- ✅ Ricerca multi-store automatica
- ✅ Espansione sinonimi intelligente (es. "pasta" → "spaghetti", "penne")
- ✅ Query multi-prodotto con conversazione
- ✅ Output formattato markdown con prezzi e supermercati

---

## 📊 Database

### Schema Tabelle

**supermercati**
- `id`, `nome`, `url`, `ultimo_scraping`

**prodotti**
- `id`, `nome`, `nome_normalizzato`, `categoria`, `marca`, `unita_misura`
- `primo_inserimento`, `ultimo_aggiornamento`

**prezzi**
- `id`, `prodotto_id`, `supermercato_id`, `prezzo`, `in_offerta`
- `prezzo_originale`, `url_prodotto`, `timestamp`

### Query Utili

```python
from src.db import PriceDatabase

db = PriceDatabase()

# Statistiche generali
stats = db.get_stats()
print(f"Prodotti totali: {stats['totale_prodotti']}")
print(f"Prezzi registrati: {stats['totale_prezzi']}")

# Cerca prodotto
prodotti = db.search_product("barilla")
for p in prodotti:
    print(f"{p['nome']} - {p['supermercato']}: €{p['prezzo']}")

# Storico prezzi
history = db.get_price_history(product_id=123)
```

---

## 🧪 Testing

```bash
# Esegui tutti i test
python tests/run_tests.py

# Test specifici
python tests/test_db.py
python tests/test_parser_utils.py
python tests/test_integration.py

# Debug Castoro
python tests/debug_scripts/explore_castoro.py
python tests/debug_scripts/test_pagination.py
```

---

## 🔍 Troubleshooting

### Errore: "selenium not found"

```bash
# Attiva ambiente virtuale
source .venv/bin/activate

# Reinstalla dipendenze
pip install -r requirements.txt
```

### Errore: "chromedriver not found"

```bash
# Raspberry Pi / ARM
sudo apt install chromium-chromedriver

# x86/x64
# Selenium 4.x installa automaticamente chromedriver
# Se necessario: pip install --upgrade selenium
```

### Database non si aggiorna

```bash
# Verifica permessi
ls -la src/prezzi.db

# Assegna permessi
chmod 664 src/prezzi.db

# Reset database (ATTENZIONE: cancella tutto)
python src/clean_db.py
```

### Cron job non funziona

```bash
# Verifica log di sistema
grep CRON /var/log/syslog | tail -20

# Test manuale script
./run_scraping.sh

# Verifica permessi esecuzione
chmod +x run_scraping.sh

# Controlla path assoluti in crontab
# ❌ SBAGLIATO: ./run_scraping.sh
# ✅ CORRETTO: /home/user/supermarket_parser/run_scraping.sh
```

### Scraping Castoro lento

```bash
# Riduci numero categorie (modifica castoro_all_urls.py)
# O aumenta timeout in config.py:
PAGE_LOAD_DELAY = 10  # Da 8 a 10 secondi
```

---

## 📈 Performance

### Tempi di Scraping

| Supermercato | Categorie | Prodotti | Tempo Stimato |
|-------------|-----------|----------|---------------|
| Eurospin | ~20 | ~350 | 15-20 min |
| Castoro Shop | 109 | 1000+ | 60-90 min |
| **TOTALE** | **129** | **~1350+** | **90-120 min** |

### Ottimizzazioni Implementate

- ✅ **Paginazione automatica**: Tutte le pagine per ogni categoria
- ✅ **Lazy loading detection**: Scroll + wait per contenuti dinamici
- ✅ **Session persistence**: Cookie salvati per 7 giorni (no login ripetuti)
- ✅ **Rate limiting**: Delay randomizzati anti-ban
- ✅ **Fuzzy matching**: Evita duplicati prodotti simili
- ✅ **Headless mode**: Nessuna interfaccia grafica (più veloce)

---

## 🛠️ Sviluppo

### Aggiungere Nuovo Supermercato

1. **Crea nuovo parser** in `src/nuovo_parser.py`:

```python
from selenium import webdriver
from src.db import PriceDatabase
from src.config import *

class NuovoParser:
    def __init__(self):
        self.db = PriceDatabase()
        self.driver = webdriver.Chrome(...)
    
    def scrape_all(self):
        # Logica scraping
        pass
    
    def _extract_product(self, element):
        # Parsing singolo prodotto
        return {
            'nome': ...,
            'prezzo': ...,
            'categoria': ...
        }
```

2. **Aggiungi a `src/scrape_all.py`**:

```python
from src.nuovo_parser import NuovoParser

def main():
    # ... parser esistenti ...
    
    print("\n=== NUOVO SUPERMERCATO ===")
    nuovo = NuovoParser()
    nuovo.scrape_all()
```

3. **Testa**:

```bash
python src/scrape_all.py
```

### Script Debug Disponibili

In `tests/debug_scripts/`:

- `explore_castoro.py` - Esplora struttura HTML sito Castoro
- `debug_castoro.py` - Debug generale parser Castoro
- `test_pagination.py` - Testa paginazione specifica categoria
- `generate_castoro_urls.py` - Genera lista URL da file categorie

---

## 📝 Log Files

I log vengono salvati in `logs/scraping_YYYYMMDD_HHMM.log`

**Contenuto:**
- Timestamp dettagliato operazioni
- Progressi per categoria
- Numero prodotti scrapati
- Errori con traceback
- Statistiche finali (totale prodotti, tempo esecuzione)

**Gestione log:**

```bash
# Visualizza ultimi 100 log
tail -100 logs/scraping_*.log

# Cerca errori specifici
grep -i "error\|exception" logs/*.log

# Pulizia vecchi log (>30 giorni)
find logs/ -name "*.log" -mtime +30 -delete

# Dimensione totale log
du -sh logs/
```

---

## 🎯 Roadmap

**Supermercati Pianificati:**
- [ ] Parser Lidl
- [ ] Parser Conad
- [ ] Parser Carrefour

**Features Future:**
- [ ] API REST per accesso esterno database
- [ ] Dashboard web interattiva (Vue.js/React)
- [ ] Notifiche Telegram per offerte
- [ ] Integrazione Home Assistant avanzata
- [ ] Machine learning previsione prezzi
- [ ] Comparazione prezzi con analisi storica
- [ ] Export CSV/Excel report

---

## 📄 Licenza

MIT License - Vedi file LICENSE

---

## 🤝 Contributi

Pull request benvenute! Per modifiche importanti:

1. Apri issue per discussione
2. Fork repository
3. Crea branch feature (`git checkout -b feature/AmazingFeature`)
4. Commit modifiche (`git commit -m 'Add AmazingFeature'`)
5. Push a branch (`git push origin feature/AmazingFeature`)
6. Apri Pull Request

---

## 📞 Supporto

**Hai problemi?**

1. Consulta sezione [Troubleshooting](#-troubleshooting)
2. Verifica [Issues GitHub](https://github.com/user/repo/issues) esistenti
3. Apri nuovo issue con:
   - Descrizione problema
   - Log errore completo
   - Sistema operativo e versione Python
   - Output `pip list`

---

**Ultimo aggiornamento**: Gennaio 2026  
**Versione**: 2.0 (Multi-Store + LLM + Paginazione)  
**Autore**: DanyM
