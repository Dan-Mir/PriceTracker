# 🛒 Supermarket Price Scraper

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-green.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema automatico di scraping multi-supermercato per confronto prezzi e analisi. Supporta Eurospin e Castoro Shop con database centralizzato e assistente LLM integrato.

---

## Descrizione
Questo progetto fornisce un sistema completo per eseguire lo scraping automatico dei prezzi da diversi supermercati italiani, tramite i loro shop online.
Utilizzando tecniche avanzate di scraping (incluso Shadow DOM e paginazione intelligente), raccoglie dati sui prodotti e li memorizza in un database SQLite. Un sistema ibrido basato su modelli LLM (FunctionGemma locale e Gemini API cloud) consente di ottimizzare le liste della spesa, offrendo alternative intelligenti basate
su ragionamento semantico. Un'interfaccia web moderna permette agli utenti di interagire facilmente con il sistema, visualizzare i dati e ottenere raccomandazioni.
L'aggiornamento dei dati è automatizzato tramite cron job, garantendo che le informazioni sui prezzi siano sempre aggiornate, e deve tenere conto anche di attuali 
promozioni e offerte speciali. Per tale motivo il DB deve essere costituito anche di campi specifici per la gestione delle offerte, come il prezzo attuale, 
rispetto al prezzo originale e al timestamp dell'ultimo aggiornamento.

L'obiettivo del progetto è fornire uno strumento potente e flessibile per confrontare i prezzi dei supermercati, aiutando gli utenti a risparmiare tempo e denaro nelle loro spese quotidiane. Questo sistema è altamente estensibile, permettendo l'aggiunta di nuovi supermercati e funzionalità in futuro.

L'utente inserisce la lista della spesa in un'interfaccia web, e il sistema deve utilizzare degli LLM per ottimizzare la spesa all'utente.

I limiti maggiori includono la dipendenza dalla struttura dei siti web dei supermercati, che può cambiare e richiedere aggiornamenti ai parser. Inoltre, alcuni
supermercati, come Eurospin, richiedono il login per accedere ai prezzi, il che può complicare lo scraping. Il sistema deve essere progettato per far fronte a queste sfide in modo robusto. Infine, un altro limite è rappresentato dalla varietà di nomi di prodotti che generalmente sono descritti in linguaggio naturale in maniera 
collettiva, ad esempio una lista della spesa contiene generalmente termini come "pasta", "latte", "legumi", "carne", mentre sul DB saranno presenti nomi di prodotti
specifici come "Fusilli Barilla 500g", "Latte parzialmente scremato UHT 1L", "Fagioli cannellini 400g". Per questo motivo è necessario un sistema di fuzzy matching e ragionamento semantico per mappare correttamente i termini generici della lista della spesa con i prodotti specifici presenti nel database.

# Stato attuale del progetto

## 📊 Panoramica

| Supermercato | Prodotti | Tecnologia | Status |
|-------------|----------|------------|--------|
| **Eurospin** | ~350 | Shadow DOM + Session | ✅ Attivo |
| **Castoro Shop** | 1000+ | Vue.js SPA + Paginazione (109 categorie) | ✅ Attivo |
| **TOTALE** | **~1350+** | SQLite Database | 🟢 Online |

**Funzionalità Principali:**
- 🔄 Scraping automatico con paginazione intelligente
- 🤖 **Sistema ibrido AI**: FunctionGemma (locale) + Gemini API (cloud)
- 🌐 **Frontend Web**: Interfaccia moderna per ottimizzare lista spesa
- 🧠 Espansione keyword intelligente con categorie database
- 📈 Database storico prezzi con tracking temporale
- 🎯 Top 3 alternative per ogni prodotto con reasoning
- ⏰ Automazione completa via cron job
- 📡 **API REST**: Backend Flask con endpoint per integrazione esterna

---

## 🚀 Quick Start

### Installazione

```bash
# Clone repository
git clone <repo-url> -b supermarket_parser
cd supermarket_parser

# Setup ambiente virtuale
python3 -m venv .venv
source .venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Configura variabili ambiente
echo "EUROSPIN_EMAIL=tua.email@esempio.com" > .env
echo "GEMINI_API_KEY=tua-api-key-gemini" >> .env
```

### Primo Utilizzo

```bash
# 1. Esegui scraping
./run_scraping.sh

# 2. Visualizza database
python src/show_db.py

# 3. Avvia frontend web
./run_server.sh
# Poi apri frontend/index.html nel browser

# 4. Oppure testa via CLI
python test_lista_spesa.py

# 5. Cerca offerte specifiche
python src/show_offers.py "pasta"
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
├── run_scraping.sh              # ⭐ Script automazione scraping
├── run_server.sh                # ⭐ Script avvio backend API
├── test_lista_spesa.py          # Test sistema AI ibrido (CLI)
├── lista_spesa.txt              # Esempio lista della spesa
├── backend/
│   └── api.py                   # 🆕 Flask API REST
├── frontend/
│   ├── index.html               # 🆕 Interfaccia web
│   ├── style.css                # 🆕 Styling responsive
│   └── app.js                   # 🆕 JavaScript frontend
├── src/
│   ├── eurospin/
│   │   └── parser.py            # Parser Eurospin (Shadow DOM)
│   ├── castoro/
│   │   ├── castoro_parser.py    # Parser Castoro (109 categorie)
│   │   ├── castoro_all_urls.py  # URL categorie
│   │   └── castoro_categories.txt
│   ├── scrape_all.py            # Orchestrator multi-store
│   ├── gemini_optimizer.py      # Ottimizzatore ibrido AI
│   ├── keyword_expander.py      # Espansione categorie
│   ├── db.py                    # Database SQLite + ricerca avanzata
│   ├── llm_interface.py         # Interfaccia FunctionGemma
│   ├── config.py                # Configurazione centralizzata
│   ├── normalizer.py            # Fuzzy matching prodotti
│   ├── utils.py                 # Utilities (retry, rate limiting)
│   ├── show_db.py               # Visualizza database
│   └── show_offers.py           # Cerca offerte
├── tests/                       # Test e debug scripts
├── logs/                        # Log scraping
└── README.md                    # Documentazione
```

---

## 🔧 Configurazione

### Variabili Ambiente (.env)

```env
# Email per login Eurospin (obbligatorio)
EUROSPIN_EMAIL=tua.email@esempio.com

# Gemini API per sistema ibrido (obbligatorio)
GEMINI_API_KEY=your-gemini-api-key

# Ollama locale (opzionale - già incluso)
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=functiongemma:latest
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

## 🤖 Sistema AI Ibrido

Architettura innovativa che combina:
- **FunctionGemma (270M)** - Locale su Raspberry Pi per estrazione keywords
- **Gemini API** - Cloud per ragionamento semantico avanzato

### Setup

```bash
# 1. Installa Ollama (per FunctionGemma locale)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull functiongemma:270m

# 2. Installa dipendenze Python
pip install google-genai ollama

# 3. Configura API key Gemini
echo "GEMINI_API_KEY=your-api-key" >> .env
# Ottieni key gratuita: https://aistudio.google.com/apikey
```

### Utilizzo

```bash
# Test con lista della spesa
python test_lista_spesa.py
```

**Come funziona:**

```
Utente: "Pasta Barilla, latte, uova"
    ↓
┌─────────────────────────┐
│ FunctionGemma (locale)  │ Estrae: ["pasta", "latte", "uova"]
│ 270M parametri          │ Query DB per categoria "Pasta"
└────────┬────────────────┘
         ↓ (20 risultati)
┌─────────────────────────┐
│ Database SQLite         │ • Pasta sfoglia €0.95
│ + Espansione categorie  │ • Penne rigate €0.73
└────────┬────────────────┘ • Fusilli €0.89
         ↓
┌─────────────────────────┐
│ Gemini API (cloud)      │ Ragionamento semantico:
│ Modello: gemini-2.0     │ ✅ "Pasta Barilla" → Penne (NON sfoglia!)
└────────┬────────────────┘ ✅ Top 3 alternative per prodotto
         ↓
📋 Output: Top 3 opzioni con prezzi e supermercati
```

**Vantaggi:**
- ✅ Leggero su Raspberry Pi (solo FunctionGemma locale)
- ✅ Ragionamento semantico accurato (Gemini cloud)
- ✅ Espansione categorie automatica
- ✅ Top 3 alternative con reasoning per ogni prodotto
- ✅ Gratuito (Gemini Free Tier: 15 req/min)

---

## 🌐 Frontend Web

### Setup

```bash
# 1. Installa dipendenze backend
pip install flask flask-cors

# 2. Avvia backend API
./run_server.sh

# 3. Apri frontend nel browser
# Vai su: frontend/index.html
# Oppure con server locale:
cd frontend
python -m http.server 8080
# Apri http://localhost:8080
```

### Utilizzo

1. **Inserisci lista della spesa** (uno per riga):
   ```
   Pasta Barilla
   Latte intero
   Uova fresche
   Pomodori pelati
   ```

2. **Clicca "Ottimizza Lista"**
   - FunctionGemma estrae keywords
   - Database ricerca con categorie espanse
   - Gemini seleziona top 3 alternative

3. **Risultati visualizzati**:
   - Top 3 prodotti per ogni query
   - Prezzo, supermercato, categoria
   - Ragionamento AI per ogni scelta
   - Esporta risultati in TXT

### API Endpoints

**Backend Flask** (porta 5000):

| Endpoint | Method | Descrizione |
|----------|--------|-------------|
| `/api/health` | GET | Health check API |
| `/api/stats` | GET | Statistiche database |
| `/api/optimize` | POST | Ottimizza lista spesa |
| `/api/search` | POST | Cerca prodotti |

**Esempio richiesta**:
```bash
curl -X POST http://localhost:5000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"items": ["pasta", "latte", "uova"]}'
```

**Risposta**:
```json
{
  "success": true,
  "data": {
    "results": [...],
    "summary": {
      "total_products": 3,
      "total_matches": 42,
      "avg_matches_per_product": 14.0
    }
  }
}
```

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