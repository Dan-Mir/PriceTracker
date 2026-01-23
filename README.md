# 🛒 Eurospin Spesa Online Scraper

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

Un crawler avanzato basato su **Selenium** per estrarre automaticamente il catalogo prodotti, i prezzi e le offerte dal sito "La Spesa Online" di Eurospin. Progettato per essere resiliente, gestire sessioni persistenti e bypassare le complessità del frontend moderno (Shadow DOM, Salesforce, Vue.js).

> **Scopo del progetto:** Creare un database storico dei prezzi per analisi dati e future integrazioni con **Home Assistant** e LLM locali (es. Gemma/Llama) per consigli sugli acquisti.

---

## ✨ Funzionalità Chiave

* **🕵️‍♂️ Navigazione Intelligente (BFS):** Utilizza un algoritmo Breadth-First Search per scansionare categorie e sottocategorie senza rimanere bloccato in loop infiniti.
* **🍪 Session Persistence:** Gestione automatica dei cookie (`cookies.pkl`) per evitare di richiedere l'OTP ad ogni avvio.
* **⚡ Shadow DOM Bypass:** Tecniche di injection JavaScript per interagire con elementi nascosti all'interno di componenti Salesforce/LWC.
* **🧹 Smart Cleaning:** Filtri regex avanzati per distinguere nomi prodotti, pesi e spazzatura (es. "Totale Carrello").
* **💾 Database SQLite:** Salvataggio strutturato e leggero dei dati in locale.
* **🔄 Paginazione Automatica:** Scorre tutte le pagine di una categoria fino all'ultimo prodotto.

---

## 📂 Struttura del Progetto

```text
supermarket_parser/
├── src/
│   ├── main.py          # Entry point dello script
│   ├── parser.py        # Logica del crawler e scraping (Selenium)
│   ├── db.py            # Gestione connessione e query SQLite
│   ├── show_db.py       # Script di utility per visualizzare i dati
│   └── clean_db.py      # Script per pulire il database
├── prezzi.db            # Database SQLite (generato automaticamente)
├── cookies.pkl          # Cookie di sessione (generato al primo login)
├── requirements.txt     # Dipendenze Python
├── setup_colab.sh       # Script di installazione per Google Colab/Linux
└── README.md            # Documentazione
```

---

## 🚀 Installazione

### Prerequisiti

- Python 3.8 o superiore
- Google Chrome installato
- ChromeDriver compatibile con la tua versione di Chrome

### 1. Clona la repository

```bash
git clone https://github.com/IL_TUO_USERNAME/eurospin-scraper.git
cd eurospin-scraper
```

### 2. Installa le dipendenze

È consigliato usare un virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Su Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 💻 Utilizzo

### Primo Avvio (Login & Setup)

La prima volta che esegui lo script, dovrai effettuare il login manuale per generare i cookie di sessione.

1. Assicurati di avere le credenziali (email) configurate o inseriscile quando richiesto.
2. Esegui lo script:

```bash
python src/main.py
```

3. Il browser si aprirà (o lavorerà in headless). Inserisci il codice OTP ricevuto via email nel terminale quando richiesto.
4. Una volta loggato, lo script salverà `cookies.pkl` e inizierà il crawling.

### Esecuzioni Successive

Rilanciando `python src/main.py`, lo script caricherà i cookie salvati e salterà la procedura di login, iniziando immediatamente a scaricare i prezzi.

### Modalità Debug con Screenshots

Per registrare screenshot durante l'esecuzione (utile per debugging):

```bash
python src/main.py --screenshots
```

Questo genererà un file `debug_video.zip` con tutti gli screenshot catturati.

### Verifica dei Dati

Per vedere cosa è stato salvato nel database:

```bash
python src/show_db.py
```

---

## 🗄️ Schema Database

Il file `prezzi.db` contiene una tabella `prodotti` con la seguente struttura:

| Colonna              | Tipo     | Descrizione                                                    |
|----------------------|----------|----------------------------------------------------------------|
| `id`                 | INTEGER  | Identificativo univoco (PK)                                    |
| `nome`               | TEXT     | Nome del prodotto (es. "Arance Navel")                        |
| `marca`              | TEXT     | Marca del prodotto (vuota se non rilevata)                    |
| `prezzo_listino`     | REAL     | Prezzo pieno (uguale a offerta se non scontato)               |
| `prezzo_offerta`     | REAL     | Prezzo attuale di vendita                                      |
| `unita_misura`       | TEXT     | Unità di misura (es. "kg", "pz")                              |
| `categoria`          | TEXT     | Categoria di appartenenza (es. "Frutta e Verdura > Frutta")  |
| `supermercato`       | TEXT     | Nome del supermercato ("Eurospin")                            |
| `data_aggiornamento` | DATETIME | Timestamp dell'ultima scansione                                |

---

## 🗺️ Roadmap & Futuro

- [x] Crawler base e paginazione
- [x] Login persistente con cookie
- [x] Salvataggio su SQLite
- [x] Gestione sessioni con cookie persistence
- [ ] Containerizzazione Docker per deployment su Raspberry Pi
- [ ] API Server (Flask/FastAPI) per esporre i dati in formato JSON
- [ ] Integrazione Home Assistant: Creazione di sensori per monitorare offerte specifiche
- [ ] Supporto LLM: Integrazione con Gemma/Llama per query in linguaggio naturale ("Dove costa meno la pasta oggi?")
- [ ] Estrazione automatica della marca dai nomi prodotto
- [ ] Supporto multi-supermercato (Conad, Coop, ecc.)

---

## ⚠️ Disclaimer

Questo progetto è stato creato **a scopo educativo e di studio** per analizzare le tecniche di web scraping su siti moderni (SPA, Shadow DOM).

**L'autore non è affiliato con Eurospin.** L'uso automatizzato di bot sui siti web potrebbe violare i Termini di Servizio. Utilizza questo script **responsabilmente**, limitando la frequenza delle richieste per non sovraccaricare i server.

---

## 📝 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.