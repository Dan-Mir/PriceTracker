# 🗺️ Piano Fase 2 - Shopping Optimizer + LLM

## 📋 Obiettivi Fase 2

### 1. Shopping List Optimizer
Data una lista della spesa, trova i 3 supermercati con il prezzo totale più basso.

### 2. LLM Integration
Assistente conversazionale con FunctionGemma (Ollama) per interrogare il database.

### 3. Parser Multi-Supermercato (opzionale, parallelo)
Aggiungere Lidl, Conad, Esselunga.

---

## 🎯 Task Fase 2

### Task 1: Shopping List Optimizer (Priorità: Alta)

**Tempo stimato:** 1-2 settimane

**File da creare:** `src/shopping_optimizer.py`

**Funzionalità:**
```python
class ShoppingOptimizer:
    def __init__(self, db: PriceDatabase):
        self.db = db
        self.normalizer = ProductNormalizer()
    
    def find_best_supermarkets(self, shopping_list: List[str], top_n=3):
        """
        Input: ['latte', 'pane', 'pasta', 'olio']
        Output: [
            {
                'supermercato': 'Eurospin',
                'prezzo_totale': 8.50,
                'disponibilita': '4/4',
                'prodotti': [
                    {'item': 'latte', 'prodotto': 'Latte Intero 1L', 'prezzo': 1.29},
                    {'item': 'pane', 'prodotto': 'Pane Bianco 500g', 'prezzo': 1.50},
                    ...
                ]
            },
            ...
        ]
        """
        results = []
        
        for supermercato in self.db.get_all_supermarkets():
            total_price = 0
            matched_products = []
            items_found = 0
            
            for item in shopping_list:
                # 1. Query prodotti dal DB per questo supermercato
                candidates = self.db.search_products(item, supermercato)
                
                # 2. Usa fuzzy matching per trovare il miglior match
                best_match = self._find_best_product(item, candidates)
                
                if best_match:
                    total_price += best_match['prezzo']
                    items_found += 1
                    matched_products.append({
                        'item': item,
                        'prodotto': best_match['nome'],
                        'prezzo': best_match['prezzo']
                    })
            
            # 3. Calcola score combinato
            availability_score = items_found / len(shopping_list)
            price_score = 1 / (total_price + 1)  # Normalizza
            
            combined_score = (
                config.RANKING_WEIGHT_PRICE * price_score +
                config.RANKING_WEIGHT_AVAILABILITY * availability_score
            )
            
            results.append({
                'supermercato': supermercato,
                'prezzo_totale': total_price,
                'disponibilita': f'{items_found}/{len(shopping_list)}',
                'prodotti': matched_products,
                'score': combined_score
            })
        
        # 4. Ordina per score e ritorna top N
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_n]
    
    def _find_best_product(self, query: str, candidates: List[dict]) -> Optional[dict]:
        """Trova il prodotto migliore usando fuzzy matching"""
        if not candidates:
            return None
        
        # Estrai i nomi dei prodotti candidati
        candidate_names = [c['nome'] for c in candidates]
        
        # Usa normalizer per trovare il miglior match
        best_match = self.normalizer.find_best_match(query, candidate_names)
        
        if best_match:
            best_name, score = best_match
            # Ritorna il prodotto completo
            for candidate in candidates:
                if candidate['nome'] == best_name:
                    return candidate
        
        # Fallback: ritorna il primo candidato (più economico)
        return candidates[0]
```

**Modifiche al DB necessarie:**

Aggiungi a `src/db.py`:
```python
def search_products(self, query: str, supermercato: str = None, limit: int = 10):
    """
    Cerca prodotti per nome (con LIKE)
    
    Args:
        query: Testo da cercare
        supermercato: Filtra per supermercato (opzionale)
        limit: Numero massimo risultati
    
    Returns:
        Lista di dict con prodotti trovati
    """
    sql = '''
        SELECT p.nome, p.marca, p.unita_misura, pr.prezzo_attuale, s.nome as supermercato
        FROM prodotti p
        JOIN prezzi pr ON p.id = pr.prodotto_id
        JOIN supermercati s ON pr.supermercato_id = s.id
        WHERE p.nome LIKE ?
          AND pr.id IN (
              SELECT MAX(id) FROM prezzi GROUP BY prodotto_id, supermercato_id
          )
    '''
    
    params = [f'%{query}%']
    
    if supermercato:
        sql += ' AND s.nome = ?'
        params.append(supermercato)
    
    sql += ' ORDER BY pr.prezzo_attuale ASC LIMIT ?'
    params.append(limit)
    
    cursor = self.conn.execute(sql, params)
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'nome': row[0],
            'marca': row[1],
            'unita_misura': row[2],
            'prezzo': row[3],
            'supermercato': row[4]
        })
    
    return results

def get_all_supermarkets(self):
    """Ottiene lista di tutti i supermercati"""
    cursor = self.conn.execute("SELECT DISTINCT nome FROM supermercati")
    return [row[0] for row in cursor.fetchall()]
```

**Script di test:** `test_optimizer.py`
```python
from shopping_optimizer import ShoppingOptimizer
from db import PriceDatabase

db = PriceDatabase()
optimizer = ShoppingOptimizer(db)

# Test 1: Lista spesa semplice
lista = ["latte", "pane", "pasta"]
results = optimizer.find_best_supermarkets(lista, top_n=3)

print("🛒 MIGLIORI SUPERMERCATI:")
for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['supermercato']}")
    print(f"   Totale: €{result['prezzo_totale']:.2f}")
    print(f"   Disponibilità: {result['disponibilita']}")
    print(f"   Prodotti:")
    for prod in result['prodotti']:
        print(f"     - {prod['item']}: {prod['prodotto']} (€{prod['prezzo']:.2f})")

db.close()
```

---

### Task 2: LLM Integration con FunctionGemma

**Tempo stimato:** 2-3 settimane

**File da creare:** `src/llm_interface.py`

**Setup preliminare:**
```bash
# 1. Installa Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Scarica modello (usa gemma2:2b, più leggero di FunctionGemma se non disponibile)
ollama pull gemma2:2b

# 3. Test modello
ollama run gemma2:2b "Ciao, dimmi qualcosa sui supermercati"

# 4. Installa libreria Ollama Python
pip install ollama
```

**Aggiorna `requirements.txt`:**
```
selenium
webdriver-manager
schedule
python-dotenv
fuzzywuzzy[speedup]
python-Levenshtein
ollama  # ← NUOVO
```

**Implementazione:**

```python
import ollama
from typing import Dict, Any, List
from db import PriceDatabase
from shopping_optimizer import ShoppingOptimizer
from logger import get_logger

logger = get_logger(__name__)


class GemmaShoppingAssistant:
    """Assistente conversazionale per la spesa con LLM"""
    
    def __init__(self, model: str = "gemma2:2b"):
        self.model = model
        self.db = PriceDatabase()
        self.optimizer = ShoppingOptimizer(self.db)
        
        # Definisci le funzioni disponibili per il LLM
        self.functions = {
            "cerca_prodotto": self.cerca_prodotto,
            "trova_offerte": self.trova_offerte,
            "ottimizza_spesa": self.ottimizza_spesa,
            "storico_prezzi": self.storico_prezzi
        }
        
        # System prompt
        self.system_prompt = """
Sei un assistente per la spesa intelligente. Hai accesso a un database di prezzi
di supermercati italiani. Puoi:

1. Cercare prodotti specifici
2. Trovare offerte attive
3. Ottimizzare una lista della spesa (trovare i 3 supermercati più economici)
4. Mostrare lo storico prezzi di un prodotto

Quando l'utente fa una domanda, usa le funzioni disponibili per rispondere.
Rispondi sempre in italiano, in modo chiaro e conciso.
"""
    
    def cerca_prodotto(self, nome_prodotto: str, supermercato: str = None) -> Dict[str, Any]:
        """Cerca un prodotto nel database"""
        logger.info(f"Cerco prodotto: {nome_prodotto} (supermercato: {supermercato or 'tutti'})")
        
        results = self.db.search_products(nome_prodotto, supermercato, limit=5)
        
        if not results:
            return {"trovati": 0, "messaggio": f"Nessun prodotto trovato per '{nome_prodotto}'"}
        
        return {
            "trovati": len(results),
            "prodotti": results
        }
    
    def trova_offerte(self, min_sconto: float = 5.0, categoria: str = None) -> Dict[str, Any]:
        """Trova prodotti in offerta"""
        logger.info(f"Cerco offerte (min sconto: {min_sconto}%, categoria: {categoria or 'tutte'})")
        
        offerte = self.db.get_products_in_offer(min_sconto=min_sconto)
        
        return {
            "offerte_trovate": len(offerte),
            "offerte": [
                {
                    "nome": o[0],
                    "marca": o[1],
                    "prezzo_prima": o[2],
                    "prezzo_ora": o[3],
                    "sconto": o[4],
                    "supermercato": o[5]
                }
                for o in offerte[:10]  # Max 10 offerte
            ]
        }
    
    def ottimizza_spesa(self, lista_spesa: List[str]) -> Dict[str, Any]:
        """Trova i 3 supermercati migliori per una lista della spesa"""
        logger.info(f"Ottimizzo spesa per: {lista_spesa}")
        
        results = self.optimizer.find_best_supermarkets(lista_spesa, top_n=3)
        
        return {
            "supermercati_migliori": len(results),
            "ranking": results
        }
    
    def storico_prezzi(self, nome_prodotto: str) -> Dict[str, Any]:
        """Ottiene lo storico prezzi di un prodotto"""
        logger.info(f"Recupero storico prezzi: {nome_prodotto}")
        
        history = self.db.get_price_history(nome_prodotto)
        
        if not history:
            return {"trovati": 0, "messaggio": f"Nessuno storico per '{nome_prodotto}'"}
        
        return {
            "rilevazioni": len(history),
            "storico": [
                {
                    "prezzo": h[0],
                    "data": h[1],
                    "supermercato": h[2]
                }
                for h in history
            ]
        }
    
    def chat(self, user_message: str) -> str:
        """
        Gestisce una conversazione con l'utente
        
        Args:
            user_message: Messaggio dell'utente
        
        Returns:
            Risposta del LLM
        """
        logger.info(f"User: {user_message}")
        
        # Costruisci il prompt con le funzioni disponibili
        prompt = f"""{self.system_prompt}

Funzioni disponibili:
1. cerca_prodotto(nome_prodotto: str, supermercato: str = None)
2. trova_offerte(min_sconto: float = 5.0, categoria: str = None)
3. ottimizza_spesa(lista_spesa: List[str])
4. storico_prezzi(nome_prodotto: str)

Domanda utente: {user_message}

Se necessario, specifica quale funzione chiamare e con quali parametri.
Formato: FUNCTION: nome_funzione(param1="valore1", param2="valore2")
Altrimenti, rispondi direttamente.
"""
        
        # Chiama LLM
        response = ollama.generate(model=self.model, prompt=prompt)
        llm_response = response['response']
        
        logger.info(f"LLM raw: {llm_response}")
        
        # Parsea la risposta per function calling
        if llm_response.startswith("FUNCTION:"):
            # Estrai chiamata funzione
            function_call = llm_response.split("FUNCTION:")[1].strip()
            logger.info(f"Function call detected: {function_call}")
            
            # Esegui la funzione (parsing semplificato)
            result = self._execute_function(function_call)
            
            # Chiedi al LLM di formattare la risposta
            format_prompt = f"""
Hai ricevuto questi dati:
{result}

Rispondi all'utente in modo chiaro e conciso in italiano, 
basandoti su questi dati. La domanda era: {user_message}
"""
            final_response = ollama.generate(model=self.model, prompt=format_prompt)
            return final_response['response']
        
        return llm_response
    
    def _execute_function(self, function_call: str) -> Any:
        """Esegue una funzione specificata dal LLM"""
        # Parsing semplificato (in produzione usare parser robusto)
        try:
            func_name = function_call.split("(")[0].strip()
            
            # Estrai parametri (parsing grezzo)
            if func_name in self.functions:
                # Per ora esegui senza parametri (implementare parser completo)
                return self.functions[func_name]()
        except Exception as e:
            logger.error(f"Errore esecuzione funzione: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Chiude le connessioni"""
        self.db.close()
```

**Script di test:** `test_llm.py`
```python
from llm_interface import GemmaShoppingAssistant

assistant = GemmaShoppingAssistant()

# Test 1: Cerca prodotto
print("Test 1: Cerca latte")
response = assistant.chat("Dove trovo il latte più economico?")
print(f"Risposta: {response}\n")

# Test 2: Ottimizza spesa
print("Test 2: Ottimizza spesa")
response = assistant.chat("Fammi la spesa per latte, pane e pasta. Quali sono i 3 supermercati migliori?")
print(f"Risposta: {response}\n")

# Test 3: Offerte
print("Test 3: Offerte")
response = assistant.chat("Quali sono le offerte attive?")
print(f"Risposta: {response}\n")

assistant.close()
```

**Note su vLLM:**
- **Non necessario** per Raspberry Pi 4 (richiede GPU CUDA)
- Ollama è ottimizzato per CPU
- Se performance insufficienti, usa modelli quantizzati (GGUF)
- Alternativa: Llama.cpp con binding Python

---

### Task 3: Parser Multi-Supermercato (Opzionale, Parallelo)

**Tempo stimato:** 1-2 settimane per parser

**Priorità supermercati:**
1. **Lidl** - Volantino sempre disponibile, struttura semplice
2. **Conad** - 3000+ punti vendita
3. **Esselunga** - Nord/Centro, API ben strutturata

**Architettura:**

File: `src/parsers/base_parser.py`
```python
from abc import ABC, abstractmethod
from db import PriceDatabase

class BaseParser(ABC):
    """Classe base per tutti i parser di supermercati"""
    
    def __init__(self):
        self.db = PriceDatabase()
        self.store_name = ""
        self.store_url = ""
    
    @abstractmethod
    def login(self, email: str = None) -> bool:
        """Esegue il login (se necessario)"""
        pass
    
    @abstractmethod
    def scrape_categories(self) -> List[str]:
        """Ottiene la lista delle categorie"""
        pass
    
    @abstractmethod
    def scrape_products(self, category: str) -> List[Dict]:
        """Scraping prodotti di una categoria"""
        pass
    
    def save_products(self, products: List[Dict]):
        """Salva prodotti nel database"""
        for product in products:
            self.db.upsert_product(
                nome=product['nome'],
                marca=product.get('marca'),
                prezzo_listino=product['prezzo_listino'],
                prezzo_attuale=product['prezzo_attuale'],
                categoria=product['categoria'],
                supermercato=self.store_name,
                unita_misura=product.get('unita_misura')
            )
    
    def close(self):
        """Chiude connessioni"""
        self.db.close()
```

File: `src/parsers/lidl_parser.py`
```python
from parsers.base_parser import BaseParser
import requests
from bs4 import BeautifulSoup

class LidlParser(BaseParser):
    """Parser per Lidl.it"""
    
    def __init__(self):
        super().__init__()
        self.store_name = "Lidl"
        self.store_url = "https://www.lidl.it"
    
    def login(self, email: str = None) -> bool:
        """Lidl non richiede login per vedere i prezzi"""
        return True
    
    def scrape_categories(self) -> List[str]:
        """Implementa scraping categorie Lidl"""
        # TODO: Implementare
        pass
    
    def scrape_products(self, category: str) -> List[Dict]:
        """Implementa scraping prodotti Lidl"""
        # TODO: Implementare
        pass
```

**Factory Pattern:** `src/parser_factory.py`
```python
class ParserFactory:
    """Factory per creare parser specifici"""
    
    @staticmethod
    def get_parser(store_name: str):
        """
        Ottiene il parser per un supermercato
        
        Args:
            store_name: Nome del supermercato (eurospin, lidl, conad, ...)
        
        Returns:
            Istanza del parser
        """
        store_name = store_name.lower()
        
        if store_name == 'eurospin':
            from parser import EurospinParser
            return EurospinParser()
        elif store_name == 'lidl':
            from parsers.lidl_parser import LidlParser
            return LidlParser()
        elif store_name == 'conad':
            from parsers.conad_parser import ConadParser
            return ConadParser()
        else:
            raise ValueError(f"Parser non disponibile per: {store_name}")
```

**Script multi-parser:** `src/scrape_all.py`
```python
from parser_factory import ParserFactory
import config

def scrape_all_supermarkets():
    """Esegue scraping di tutti i supermercati configurati"""
    
    supermarkets = ["eurospin", "lidl", "conad"]
    
    for store in supermarkets:
        print(f"\n🛒 Scraping {store.upper()}...")
        try:
            parser = ParserFactory.get_parser(store)
            
            # Login se necessario
            if hasattr(parser, 'login_interattivo'):
                parser.login_interattivo(config.get(f"{store.upper()}_EMAIL"))
            
            # Scraping
            parser.naviga_e_salva()
            
            parser.close()
            print(f"✅ {store.upper()} completato")
        except Exception as e:
            print(f"❌ Errore {store}: {e}")

if __name__ == "__main__":
    scrape_all_supermarkets()
```

---

## 📊 Timeline Proposta

### Settimana 1-2: Shopping Optimizer
- ✅ Implementa `shopping_optimizer.py`
- ✅ Aggiungi metodi DB necessari
- ✅ Test con dati esistenti
- ✅ Script di esempio

### Settimana 3-5: LLM Integration
- ✅ Setup Ollama + modello
- ✅ Implementa `llm_interface.py`
- ✅ Function calling robusto
- ✅ Test conversazionali
- ✅ Ottimizza prompt

### Parallelo/Continuo: Multi-Supermercato
- ✅ Crea `BaseParser`
- ✅ Implementa `LidlParser` (priorità 1)
- ✅ Implementa `ConadParser` (priorità 2)
- ✅ Factory pattern
- ✅ Script unificato

---

## 🧪 Test di Accettazione Fase 2

Al termine della Fase 2, questi scenari devono funzionare:

### Scenario 1: Shopping Optimizer CLI
```bash
$ python test_optimizer.py
Lista spesa: ['latte', 'pane', 'pasta', 'olio']

🛒 MIGLIORI SUPERMERCATI:
1. Eurospin - €8.50 (4/4 prodotti)
2. Lidl - €9.20 (4/4 prodotti)
3. Conad - €9.80 (3/4 prodotti)
```

### Scenario 2: LLM Chat
```bash
$ python test_llm.py
User: Dove trovo il latte più economico?
Assistant: Il latte più economico è all'Eurospin, a €1.29 al litro.
          Si tratta del Latte Intero UHT Parmalat.

User: Fammi la spesa per latte, pane e pasta
Assistant: Ti conviene andare all'Eurospin. Spenderai €4.80 totale:
           - Latte Intero 1L: €1.29
           - Pane Bianco 500g: €1.50
           - Pasta Barilla 500g: €2.01
```

### Scenario 3: Multi-Supermercato
```bash
$ python src/scrape_all.py
🛒 Scraping EUROSPIN...
✅ EUROSPIN completato (342 prodotti)

🛒 Scraping LIDL...
✅ LIDL completato (287 prodotti)

🛒 Scraping CONAD...
✅ CONAD completato (419 prodotti)
```

---

## 🎯 Deliverable Fase 2

1. ✅ `src/shopping_optimizer.py` - Modulo optimizer
2. ✅ `src/llm_interface.py` - Interfaccia LLM
3. ✅ `src/parsers/base_parser.py` - Classe base parser
4. ✅ `src/parsers/lidl_parser.py` - Parser Lidl
5. ✅ `src/parser_factory.py` - Factory pattern
6. ✅ `test_optimizer.py` - Test optimizer
7. ✅ `test_llm.py` - Test LLM
8. ✅ `FASE2_DOCS.md` - Documentazione Fase 2

---

## 💡 Note Implementative

### Performance LLM su Raspberry Pi 4

**Hardware:**
- CPU: Broadcom BCM2711 (4 core, 1.5 GHz)
- RAM: 4GB/8GB

**Modelli consigliati:**
1. `gemma2:2b` - 2 billion parametri, veloce (~5 token/sec)
2. `tinyllama:1.1b` - 1.1B parametri, molto veloce (~8 token/sec)
3. `phi-2` - 2.7B parametri, buona qualità (~3 token/sec)

**Quantizzazione:**
- Q4 (4-bit) - Buon compromesso qualità/velocità
- Q8 (8-bit) - Migliore qualità, più lento

**Ottimizzazioni:**
- Usa `num_ctx=512` (context window ridotto)
- Limita `num_predict=100` (max token generati)
- Batch size=1 (no batching)

### Database Ottimizzazioni

Per query veloci con fuzzy matching:

```sql
-- Crea indice full-text (SQLite FTS5)
CREATE VIRTUAL TABLE prodotti_fts USING fts5(
    nome,
    marca,
    content=prodotti,
    content_rowid=id
);

-- Trigger per sincronizzazione
CREATE TRIGGER prodotti_ai AFTER INSERT ON prodotti BEGIN
    INSERT INTO prodotti_fts(rowid, nome, marca) 
    VALUES (new.id, new.nome, new.marca);
END;
```

Query più veloce:
```python
def search_products_fts(self, query: str):
    """Ricerca full-text veloce"""
    cursor = self.conn.execute("""
        SELECT p.* FROM prodotti p
        JOIN prodotti_fts fts ON p.id = fts.rowid
        WHERE prodotti_fts MATCH ?
        ORDER BY rank
    """, (query,))
    return cursor.fetchall()
```

---

Vuoi che inizi subito con l'implementazione della Fase 2, partendo dallo Shopping Optimizer? 🚀
