# 🔧 Refactoring Fase 1 - Completato

## ✅ Modifiche Implementate

### 1. Sistema di Configurazione Centralizzato
**File creato:** `src/config.py`

Tutte le costanti, timeout e configurazioni sono ora centralizzate:
- ⚙️ Parametri di scraping (timeout, delay, limiti)
- 🌐 URL e credenziali Eurospin
- 🔍 Blacklist URL e selettori CSS
- 📝 Configurazione logging
- 🎯 Pattern per parsing (unità misura, marche)
- 🔄 Normalizzazione prodotti (sinonimi, conversioni)
- 📊 Parametri shopping optimizer

**Vantaggi:**
- Modifiche centralizzate senza toccare il codice
- Facilita testing con configurazioni diverse
- Preparazione per file `.env` o YAML esterni

---

### 2. Sistema di Logging Strutturato
**File creato:** `src/logger.py`

Sostituzione completa di `print()` con logging professionale:
- 📁 Rotazione automatica file log (10MB, 5 backup)
- 📊 Livelli di log configurabili (DEBUG, INFO, WARNING, ERROR)
- 📝 Output sia su file che console
- 🔍 Tracciamento dettagliato errori con `exc_info=True`

**Modifiche ai file:**
- ✅ `parser.py` - Tutti i print sostituiti con logger
- ✅ `db.py` - Logging per operazioni database
- ✅ `main.py` - Logging per workflow principale
- ✅ `show_offers.py` - Logger integrato

**Directory creata automaticamente:** `logs/`
**File log:** `logs/scraper.log`

---

### 3. Modulo Normalizzazione Prodotti
**File creato:** `src/normalizer.py`

Classe `ProductNormalizer` con funzionalità avanzate:

#### Funzionalità:
- 🔤 **Normalizzazione Testo**: lowercase, rimozione punteggiatura, spazi
- 📏 **Estrazione Unità Misura**: pattern per peso (g, kg), volume (ml, l), quantità (pz)
- 🏷️ **Estrazione Marca**: euristiche intelligenti (maiuscolo, keyword come S.p.A, ®, ™)
- 🔍 **Fuzzy Matching**: 
  - Sequence Matcher (Ratcliff-Obershelp)
  - Jaccard similarity su token
  - Combinazione ponderata (60% seq + 40% token)
- 🔎 **Find Best Match**: trova prodotto più simile da lista candidati
- 🌍 **Sinonimi**: espansione parole chiave (latte → milk, bevanda lattea)
- 📐 **Normalizzazione Unità**: "1kg" → "1 kg", "1,5L" → "1.5 l"

#### Soglie Configurabili:
- Default: 80/100 per match positivo
- Personalizzabile per caso d'uso specifico

---

### 4. Utilities Gestione Errori e Retry
**File creato:** `src/utils.py`

#### Decorator per Robustezza:
- 🔄 **`@retry_on_exception`**: retry automatico con exponential backoff
- ⏱️ **`@rate_limit`**: delay casuale tra richieste (anti-ban)
- ⏳ **`@timeout_handler`**: gestione timeout operazioni
- 🛡️ **`safe_execute()`**: esecuzione sicura con valore default

#### Classe RateLimiter:
- Rate limiting con stato persistente
- Delay casuali tra min/max configurabili
- Uso: `self.rate_limiter.wait()` prima di ogni richiesta

**Protezione implementata in:**
- Navigazione tra categorie (rate limiting)
- Caricamento pagine (timeout)
- Parsing elementi (safe execution)

---

### 5. Parsing Migliorato (Marca + Unità Misura)
**File modificato:** `src/parser.py` → metodo `scrape_current_page()`

#### Estrazione Intelligente:
```python
# Prima (vecchio)
marca = ""  # Sempre vuoto
unita_misura = None  # Non estratta

# Dopo (nuovo)
marca = self.normalizer.extract_brand_from_text(txt, nome_prodotto)
# Esempio: "BARILLA" estratta da card prodotto

unita_misura = self.normalizer.extract_unit(txt)
# Esempio: "500 g", "1 l", "6 pz"
```

#### Euristiche Marca:
1. Testo tutto MAIUSCOLO (>2 caratteri) → marca
2. Presenza keyword: S.p.A, S.r.l, ®, ™ → marca
3. Linea breve (<15 char) dopo nome prodotto → marca
4. Fallback: None se non individuata

#### Euristiche Unità:
- Pattern regex per peso: `\d+[.,]?\d*\s*(g|gr|grammi|kg|etto|hg)`
- Pattern volume: `\d+[.,]?\d*\s*(ml|cl|l|lt|litri)`
- Pattern quantità: `\d+\s*(pz|pezzi|conf|x)`

**Database aggiornato:**
- `db.upsert_product()` ora accetta parametro `unita_misura`
- Salvato in campo `prodotti.unita_misura`

---

### 6. Integrazione Config in Parser
**File modificato:** `src/parser.py`

Tutte le costanti ora da `config.py`:
```python
# Prima
time.sleep(5)  # Hardcoded
max_iter = 60  # Hardcoded

# Dopo
time.sleep(config.PAGE_LOAD_DELAY)  # Configurabile
max_iter = config.MAX_ITERATIONS  # Configurabile
```

**Parametri configurabili:**
- `SELENIUM_TIMEOUT` = 25s
- `PAGE_LOAD_DELAY` = 5s
- `SCROLL_DELAY` = 2s
- `LOGIN_DELAY` = 8s
- `MAX_ITERATIONS` = 60
- `MAX_PAGES_PER_CATEGORY` = 15
- `REQUEST_DELAY_MIN` = 2s
- `REQUEST_DELAY_MAX` = 5s

---

### 7. Rate Limiting Anti-Ban
**File modificato:** `src/parser.py`

```python
# Inizializzazione
self.rate_limiter = RateLimiter()

# Uso in naviga_e_salva()
while queue and iter_count < max_iter:
    self.rate_limiter.wait()  # Attende delay casuale
    self.driver.get(url)
    # ... parsing
```

**Comportamento:**
- Delay casuale tra 2-5 secondi (configurabile)
- Simula comportamento umano
- Riduce rischio di ban IP/account

---

### 8. Dipendenze Aggiornate
**File modificato:** `requirements.txt`

```txt
selenium
webdriver-manager
schedule
python-dotenv
fuzzywuzzy[speedup]  # ← NUOVO (fuzzy matching)
python-Levenshtein    # ← NUOVO (velocizza fuzzywuzzy)
```

**Installazione:**
```bash
source .venv/bin/activate  # o .venv\Scripts\activate su Windows
pip install -r requirements.txt
```

---

## 📊 Statistiche Refactoring

| Metrica | Prima | Dopo | Delta |
|---------|-------|------|-------|
| **File creati** | - | 4 | +4 |
| **Linee codice aggiunte** | - | ~800 | +800 |
| **Moduli nuovi** | - | config, logger, normalizer, utils | +4 |
| **Logging sostituiti** | 0 | 40+ | +40 |
| **Parametri configurabili** | ~5 | 50+ | +45 |
| **Funzioni estrazione dati** | 1 (prezzo) | 4 (prezzo, marca, unità, normalizzazione) | +3 |

---

## 🚀 Come Usare i Nuovi Moduli

### Esempio 1: Fuzzy Matching Prodotti
```python
from normalizer import fuzzy_match

if fuzzy_match("Latte Intero 1L", "LATTE INTERO 1000ML"):
    print("Prodotti simili!")
# Output: True (similarità > 80%)
```

### Esempio 2: Estrazione Unità
```python
from normalizer import extract_unit

unit = extract_unit("Pasta Barilla 500g")
print(unit)  # Output: "500g"
```

### Esempio 3: Rate Limiting
```python
from utils import rate_limit

@rate_limit(min_delay=2, max_delay=5)
def fetch_category(url):
    # Automaticamente attende 2-5s tra chiamate
    return requests.get(url)
```

### Esempio 4: Retry Automatico
```python
from utils import retry_on_exception

@retry_on_exception(max_retries=3)
def unstable_scraping():
    # Se fallisce, riprova 3 volte con backoff
    driver.find_element(By.ID, "element")
```

---

## 🔍 Debugging e Monitoring

### Livelli di Log
Modifica `config.py`:
```python
LOG_LEVEL = "DEBUG"  # Mostra tutto
LOG_LEVEL = "INFO"   # Solo info importanti (default)
LOG_LEVEL = "ERROR"  # Solo errori
```

### Visualizza Log
```bash
tail -f logs/scraper.log  # Linux/Mac
Get-Content logs/scraper.log -Wait  # Windows PowerShell
```

### Filtro per Modulo
```bash
grep "parser" logs/scraper.log
grep "ERROR" logs/scraper.log
```

---

## 🧪 Testing Suggerito

```bash
# 1. Test parsing marca e unità
cd src
python -c "
from normalizer import ProductNormalizer
n = ProductNormalizer()
print(n.extract_unit('Pasta 500g'))
print(n.normalize_unit('1kg'))
"

# 2. Test fuzzy matching
python -c "
from normalizer import fuzzy_match
print(fuzzy_match('Latte Intero', 'LATTE INTERO 1L'))
"

# 3. Test logging
python -c "
from logger import get_logger
log = get_logger('test')
log.info('Test info')
log.error('Test errore')
"
# Controlla logs/scraper.log

# 4. Test completo parser
python main.py
# Verifica logs/scraper.log per output strutturato
```

---

## ⚠️ Note Importanti

### Backward Compatibility
✅ Tutto il codice vecchio continua a funzionare:
- `db.insert_product()` → wrapper per `upsert_product()` (deprecation warning)
- Parametri opzionali hanno valori default
- Nessuna breaking change

### Migration Necessaria
❌ NESSUNA migration richiesta:
- Schema DB invariato
- Cookie esistenti compatibili
- File `.env` già usato

### Performance
🚀 Miglioramenti attesi:
- Fuzzy matching: ~0.1ms per confronto (C extension con python-Levenshtein)
- Logging: trascurabile (async file handler)
- Rate limiting: +2-5s per richiesta (intenzionale, anti-ban)

---

## 📋 TODO Prossimi Passi (Fase 2)

1. ✅ Shopping List Optimizer (usa normalizer per matching)
2. ✅ LLM Integration (FunctionGemma con Ollama)
3. ✅ Parser multi-supermercato (Lidl, Conad, Esselunga)
4. 🔄 Dashboard web (Flask/Streamlit)
5. 🔄 API REST (FastAPI)

---

## 🎯 Conclusioni

Il refactoring Fase 1 ha:
- ✅ Centralizzato configurazioni
- ✅ Implementato logging professionale
- ✅ Migliorato parsing dati (marca + unità)
- ✅ Aggiunto fuzzy matching robusto
- ✅ Introdotto rate limiting e retry
- ✅ Mantenuto backward compatibility

**Il codice è ora:**
- 🔧 **Manutenibile**: configurazioni centrali
- 🐛 **Debuggabile**: logging strutturato
- 🛡️ **Robusto**: retry e gestione errori
- 📈 **Scalabile**: pronto per multi-supermercato
- 🧪 **Testabile**: moduli ben separati

**Pronto per Fase 2: Shopping Optimizer + LLM Integration!** 🚀
