# 🛒 Eurospin Spesa Online Scraper

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

Un crawler avanzato basato su **Selenium** per estrarre automaticamente il catalogo prodotti, i prezzi e le offerte dal sito "La Spesa Online" di Eurospin. Progettato per essere resiliente, gestire sessioni persistenti e bypassare le complessità del frontend moderno (Shadow DOM, Salesforce, Vue.js).

> **Scopo del progetto:** Creare un database storico dei prezzi per analisi dati e future integrazioni con **Home Assistant** e LLM locali (es. Gemma/Llama) per consigli sugli acquisti.

---

## ✨ Funzionalità Chiave

* **🕵️‍♂️ Navigazione Intelligente (BFS):** Algoritmo Breadth-First Search per scansionare categorie senza loop infiniti
* **🔐 Session Persistence Completa:** Cookie + localStorage + sessionStorage per login automatico (~7 giorni senza OTP)
* **⚡ Shadow DOM Bypass:** JavaScript injection per elementi Salesforce/LWC nascosti
* **📊 Database Normalizzato:** Schema relazionale con tracking storico prezzi e offerte automatiche
* **⏱️ Timestamp Intelligenti:** Tracciamento automatico prima registrazione e ultimo update per prodotto
* **🤖 Automazione:** Supporto Windows Task Scheduler e Python scheduler per esecuzione periodica
* **🧪 Test Coverage:** Suite completa di 25 test unitari e integrazione

---

## 📂 Struttura del Progetto

```text
supermarket_parser/
├── src/
│   ├── main.py           # Entry point dello script
│   ├── parser.py         # Web scraper con Selenium + BFS crawler
│   ├── db.py             # Database layer con schema normalizzato
│   ├── scheduler.py      # Automazione Python (cron-like)
│   ├── show_db.py        # Visualizza contenuto database
│   ├── show_offers.py    # Mostra prodotti in offerta
│   └── clean_db.py       # Pulizia database
├── tests/
│   ├── test_db.py        # Test database operations
│   ├── test_parser_utils.py  # Test parsing utilities
│   ├── test_integration.py   # Test integrazione
│   └── run_tests.py      # Test runner
├── README.md             # Documentazione principale
├── AUTOMAZIONE.md        # Guida setup automazione
├── SUPERMERCATI.md       # Roadmap multi-supermercato
├── requirements.txt      # Dipendenze Python
├── run_scraping.bat      # Script Windows per Task Scheduler
└── .gitignore            # File esclusi da git
```

---

## 🚀 Installazione

### Prerequisiti

- Python 3.8 o superiore
- Google Chrome installato
- ChromeDriver compatibile con la tua versione di Chrome

### 1. Clona la repository

```bash
git clone https://github.com/TUO_USERNAME/supermarket_parser.git
cd supermarket_parser
```

### 2. Crea virtual environment

```bash
python -m venv .venv

# Linux/Mac/Raspberry Pi
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Installa dipendenze

```bash
pip install -r requirements.txt
```

---

## 💻 Utilizzo

### Primo Avvio (Login OTP)

```bash
cd src
python main.py
```

1. Inserisci email quando richiesto
2. Ricevi OTP via email
3. Inserisci codice OTP nel terminale
4. **Sessione salvata** (cookie + localStorage + sessionStorage) → valida ~7 giorni

### Esecuzioni Successive (SENZA OTP)

```bash
python main.py  # Login automatico, nessun OTP richiesto
```

### Automazione

**Windows (Task Scheduler):**
```powershell
# Test manuale
.\run_scraping.bat

# Setup automatico (vedi AUTOMAZIONE.md)
```

**Linux/Raspberry Pi (cron):**
```bash
# Esecuzione giornaliera ore 3:00
crontab -e
# Aggiungi: 0 3 * * * /path/to/.venv/bin/python /path/to/src/main.py >> /path/to/scraping.log 2>&1
```

**Python Scheduler:**
```bash
cd src
python scheduler.py  # Loop continuo con scheduling configurabile
```

### Visualizza Dati

```bash
# Statistiche database
python src/show_db.py

# Prodotti in offerta
python src/show_offers.py

# Pulizia database
python src/clean_db.py
```

### Test Suite

```bash
cd tests
python run_tests.py  # Esegue 25 test (database, parser, integrazione)
```

---

## 🗄️ Schema Database

Database SQLite normalizzato con 3 tabelle:

### Tabella `prodotti`
| Colonna | Tipo | Descrizione |
|---------|------|-------------|
| `id` | INTEGER | Primary key |
| `nome` | TEXT | Nome prodotto |
| `marca` | TEXT | Marca (nullable) |
| `categoria` | TEXT | Categoria/sottocategoria |
| `unita_misura` | TEXT | Peso/unità (es. "500g", "1L") |
| `codice_prodotto` | TEXT | Hash MD5 univoco (nome+marca+unità) |
| `data_creazione` | DATETIME | **Timestamp prima registrazione** |
| `data_ultimo_update` | DATETIME | **Timestamp ultimo scraping** |

### Tabella `prezzi`
| Colonna | Tipo | Descrizione |
|---------|------|-------------|
| `id` | INTEGER | Primary key |
| `prodotto_id` | INTEGER | FK → prodotti |
| `supermercato_id` | INTEGER | FK → supermercati |
| `prezzo_listino` | REAL | Prezzo pieno |
| `prezzo_attuale` | REAL | Prezzo di vendita |
| `in_offerta` | BOOLEAN | True se scontato |
| `sconto_percentuale` | REAL | % sconto calcolato |
| `data_rilevazione` | DATETIME | Timestamp rilevazione |

### Tabella `supermercati`
| Colonna | Tipo | Descrizione |
|---------|------|-------------|
| `id` | INTEGER | Primary key |
| `nome` | TEXT | Nome supermercato (UNIQUE) |
| `citta` | TEXT | Località (nullable) |
| `ultimo_scraping` | DATETIME | Timestamp ultimo scraping |

### Logica Upsert Intelligente
- **Nuovo prodotto**: Inserimento con `data_creazione = NOW()`
- **Prodotto esistente**: Update solo `data_ultimo_update = NOW()`
- **Nuovo record prezzo**: Solo se prezzo cambiato O passate >24h
- **Rilevamento offerte**: Automatico se `prezzo_attuale < prezzo_listino`

---

## 🗺️ Roadmap

- [x] Crawler BFS con paginazione automatica
- [x] Login persistente (cookie + localStorage + sessionStorage)
- [x] Database normalizzato con storico prezzi
- [x] Timestamp tracking (creazione + ultimo update)
- [x] Rilevamento offerte automatico
- [x] Suite completa di test (25 test)
- [x] Automazione Windows/Linux
- [ ] **Deploy su Raspberry Pi** ← Prossimo step
- [ ] API REST (Flask/FastAPI) per esposizione dati
- [ ] Dashboard web per visualizzazione offerte
- [ ] Multi-supermercato (Lidl, Conad, Esselunga - vedi SUPERMERCATI.md)
- [ ] Integrazione Home Assistant
- [ ] Query LLM (Gemma/Llama) per consigli spesa

Vedi [SUPERMERCATI.md](SUPERMERCATI.md) per roadmap dettagliata multi-store.

---

## ⚠️ Disclaimer

Questo progetto è stato creato **a scopo educativo e di studio** per analizzare le tecniche di web scraping su siti moderni (SPA, Shadow DOM).

**L'autore non è affiliato con Eurospin.** L'uso automatizzato di bot sui siti web potrebbe violare i Termini di Servizio. Utilizza questo script **responsabilmente**, limitando la frequenza delle richieste per non sovraccaricare i server.

---

## 📝 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.