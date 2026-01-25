# Fase 2: Shopping Optimizer con LLM 🤖

Guida completa all'utilizzo dell'assistente intelligente per la spesa.

## 📦 Installazione Ollama

### Su Raspberry Pi / Linux
```bash
# 1. Installa Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Avvia il server Ollama (in background)
ollama serve &

# 3. Scarica il modello LLM (consigliato per RPi4)
ollama pull gemma2:2b

# OPPURE per un modello più leggero:
ollama pull tinyllama:1.1b

# 4. Testa il modello
ollama run gemma2:2b "Ciao, come stai?"
```

### Requisiti Python
```bash
# Installa le dipendenze
cd /home/danym/Desktop/supermarket_parser
pip install -r requirements.txt
```

---

## 🛒 Modalità 1: Lista Spesa da File TXT

### Crea la tua lista spesa

Modifica il file `lista_spesa.txt`:
```txt
# Lista della spesa - 14/01/2025
latte intero
pane bianco
pasta barilla
olio extravergine
pomodori pelati
mozzarella
prosciutto crudo
yogurt magro
biscotti
acqua naturale
```

### Ottimizza la spesa (senza LLM)
```bash
cd /home/danym/Desktop/supermarket_parser
python src/optimize_shopping.py
```

**Output esempio:**
```
🛒 OTTIMIZZAZIONE LISTA SPESA
═══════════════════════════════════════════════

📝 Prodotti richiesti (10):
  1. latte intero
  2. pane bianco
  3. pasta barilla
  ...

🏆 TOP 3 SUPERMERCATI CONSIGLIATI
═══════════════════════════════════════════════

🥇 1° - Eurospin (Score: 85.3)
   💰 Costo totale: €12.45
   📦 Prodotti trovati: 8/10 (80%)
   
   Prodotti:
   ├─ latte intero               €0.99  ✓
   ├─ pane bianco                €0.89  ✓
   ├─ pasta barilla              €0.79  ✓
   ...
```

---

## 🤖 Modalità 2: Chat Interattiva con LLM

### Avvia la chat
```bash
cd /home/danym/Desktop/supermarket_parser
python src/llm_interface.py
```

### Esempi di domande

**Cerca prodotti:**
```
Tu: Dove trovo il latte più economico?
Assistente: Ho trovato 5 prodotti "latte":

1. Latte Intero Parmalat (1L) - €0.89 @ Eurospin
2. Latte Parzialmente Scremato (1L) - €0.95 @ Eurospin
...
```

**Lista della spesa naturale:**
```
Tu: La mia lista comprende: pane, uova e legumi. Cosa posso comprare?
Assistente: 💡 Per: pane, uova, legumi

🛒 Supermercati migliori:
1. Eurospin
   💰 Totale: €2.45
   ✅ 3/3
```

**Query multiple:**
```
Tu: Mostrami anche le uova e i legumi
Assistente: 
🔍 UOVA:
   1. Pappardelle all'uovo → €1.29

🔍 LEGUMI:
   1. Fagioli bianchi → €0.59
   2. Ceci lessati → €0.85
```

**Offerte:**
```
Tu: Quali sono le migliori offerte oggi?
Assistente: Ho trovato 12 offerte con sconto superiore al 5%:

1. Pasta Barilla (500g) - SCONTO 20%
   Da €1.29 → €0.99
   📍 Eurospin
   
2. Olio Carapelli (1L) - SCONTO 15%
   Da €7.99 → €6.79
   📍 Eurospin
...
```

**Ottimizza la spesa:**
```
Tu: Voglio comprare latte, pane e pasta. Dove conviene?
Assistente: Ho analizzato 1 supermercato per 3 prodotti:

🥇 Supermercato migliore: Eurospin
   💰 Costo totale: €2.67
   📦 Prodotti trovati: 3/3 (100%)
   
   Dettagli:
   - latte intero: €0.99
   - pane bianco: €0.89
   - pasta barilla: €0.79
```

**Storico prezzi:**
```
Tu: Come è cambiato il prezzo della pasta?
Assistente: Ecco lo storico prezzi per "pasta":

📊 Pasta Barilla (500g):
   - 14/01/2025: €0.99 (Eurospin)
   - 07/01/2025: €1.29 (Eurospin)
   - 31/12/2024: €1.19 (Eurospin)
```

---

## 🔧 Utilizzo Programmatico

### Da Python

```python
from src.llm_interface import GemmaShoppingAssistant

# Inizializza assistente
assistant = GemmaShoppingAssistant(model="gemma2:2b")

# Fai una domanda
risposta = assistant.chat("Dove trovo il latte più economico?")
print(risposta)

# Ottimizza lista spesa
risposta = assistant.chat("Trova latte, pane e pasta al prezzo migliore")
print(risposta)

# Chiudi connessioni
assistant.close()
```

### Chiamate Dirette

```python
# Cerca prodotto
result = assistant.cerca_prodotto("latte", supermercato="Eurospin")
print(result)
# Output: {'trovati': 5, 'prodotti': [...]}

# Offerte
offerte = assistant.trova_offerte(min_sconto=10.0)
print(offerte)
# Output: {'offerte_trovate': 8, 'offerte': [...]}

# Ottimizza spesa
ranking = assistant.ottimizza_spesa(["latte", "pane", "pasta"])
print(ranking)
# Output: {'supermercati_migliori': 1, 'ranking': [...]}

# Storico
storico = assistant.storico_prezzi("latte")
print(storico)
# Output: {'rilevazioni': 15, 'storico': [...]}
```

---

## 🎯 Funzioni LLM Disponibili

Il modello LLM può chiamare queste funzioni automaticamente:

### 1. CERCA_PRODOTTO
```python
CERCA_PRODOTTO(nome_prodotto="latte", supermercato="Eurospin")
```
- Cerca prodotti per nome (fuzzy matching)
- Filtra per supermercato (opzionale)
- Ritorna fino a 5 risultati ordinati per prezzo

### 2. TROVA_OFFERTE
```python
TROVA_OFFERTE(min_sconto=10.0)
```
- Trova prodotti in offerta
- Filtra per sconto minimo percentuale
- Ritorna fino a 10 offerte ordinate per sconto

### 3. OTTIMIZZA_SPESA
```python
OTTIMIZZA_SPESA(lista_prodotti=["latte", "pane", "pasta"])
```
- Trova i 3 supermercati migliori
- Usa fuzzy matching per identificare prodotti
- Punteggio combinato: 70% prezzo + 30% disponibilità

### 4. STORICO_PREZZI
```python
STORICO_PREZZI(nome_prodotto="latte")
```
- Mostra storico prezzi prodotto
- Fino a 30 rilevazioni
- Ordinate per data (più recenti prima)

---

## 📊 Configurazione

### Config LLM (`src/config.py`)

Aggiungi questi parametri se necessario:

```python
# LLM Settings
LLM_MODEL = "gemma2:2b"  # o "tinyllama:1.1b" per RPi4
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 512

# Shopping Optimizer Settings
RANKING_WEIGHT_PRICE = 0.7  # Peso prezzo nel ranking
RANKING_WEIGHT_AVAILABILITY = 0.3  # Peso disponibilità
FUZZY_MATCH_THRESHOLD = 80  # Soglia fuzzy matching (0-100)
```

---

## 🧪 Testing

### Test manuale
```bash
# Test chat interattiva
python src/llm_interface.py

# Test optimizer senza LLM
python src/optimize_shopping.py
```

### Test automatico (TODO)
```bash
python tests/test_llm_integration.py
```

---

## 🚀 Prossimi Passi

### Fase 2 Completa
- ✅ Shopping optimizer (fuzzy matching)
- ✅ LLM interface con function calling
- ✅ CLI interattiva
- ⏳ Test automatici

### Fase 3 (Futuro)
- [ ] Multi-supermarket parsers (Lidl, Conad, Esselunga)
- [ ] UI web (dashboard React/Vue)
- [ ] Notifiche offerte personalizzate
- [ ] Export PDF/Excel lista spesa ottimizzata

---

## 🐛 Troubleshooting

### "Ollama non disponibile"
```bash
# Verifica che Ollama sia installato
which ollama

# Verifica che il server sia avviato
curl http://localhost:11434/api/tags

# Riavvia il server
killall ollama
ollama serve &
```

### "Modello non trovato"
```bash
# Lista modelli installati
ollama list

# Scarica il modello
ollama pull gemma2:2b
```

### "Nessun prodotto trovato"
```bash
# Verifica che il database abbia dati
python src/show_db.py

# Se vuoto, esegui scraping
python src/main.py
```

### Performance lente su RPi4
```bash
# Usa un modello più leggero
ollama pull tinyllama:1.1b

# Modifica src/llm_interface.py:
assistant = GemmaShoppingAssistant(model="tinyllama:1.1b")
```

---

## 📚 Riferimenti

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Gemma2 Model Card](https://ollama.com/library/gemma2)
- [TinyLlama Model](https://ollama.com/library/tinyllama)

---

**Autore:** Dany Mirto  
**Progetto:** Supermarket Price Scraper & Optimizer  
**Versione:** 2.0 (Fase 2 - LLM Integration)
