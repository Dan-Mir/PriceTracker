"""
Interfaccia LLM con Ollama per query intelligenti sul database spesa
"""
import json
import re
from typing import Dict, Any, List, Optional

try:
    from db import PriceDatabase
    from shopping_optimizer import ShoppingOptimizer
    from logger import get_logger
except ImportError:
    from src.db import PriceDatabase
    from src.shopping_optimizer import ShoppingOptimizer
    from src.logger import get_logger

logger = get_logger(__name__)

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama non installato. Installa con: pip install ollama")


class GemmaShoppingAssistant:
    """Assistente conversazionale per la spesa con LLM"""
    
    def __init__(self, model: str = None):
        if not OLLAMA_AVAILABLE:
            raise ImportError("Ollama non disponibile. Installa con: pip install ollama")
        
        # Usa il modello da config se non specificato
        if model is None:
            try:
                from config import LLM_MODEL
                model = LLM_MODEL
            except ImportError:
                from src.config import LLM_MODEL
                model = LLM_MODEL
        
        self.model = model
        self.db = PriceDatabase()
        self.optimizer = ShoppingOptimizer(self.db)
        
        logger.info(f"GemmaShoppingAssistant inizializzato con modello: {model}")
        
        # System prompt ottimizzato per FunctionGemma
        self.system_prompt = """Sei un assistente per la spesa in Italia. Hai accesso a un database di prezzi di supermercati.

Quando l'utente chiede informazioni sui prodotti, devi chiamare le funzioni disponibili.

FUNZIONI DISPONIBILI:
- cerca_prodotto(nome_prodotto, supermercato=None) : cerca prodotti per nome
- trova_offerte(min_sconto=5.0) : trova prodotti in offerta con sconto minimo
- ottimizza_spesa(lista_prodotti) : trova i migliori supermercati per una lista
- storico_prezzi(nome_prodotto) : mostra lo storico prezzi di un prodotto

ESEMPI:
Utente: "Dove trovo il latte?"
Risposta: FUNCTION: cerca_prodotto(nome_prodotto="latte")

Utente: "Quali sono le offerte?"
Risposta: FUNCTION: trova_offerte(min_sconto=5.0)

Utente: "Voglio comprare latte, pane e pasta"
Risposta: FUNCTION: ottimizza_spesa(lista_prodotti=["latte", "pane", "pasta"])

Indaga anche sulle varie tipologie che un prodotto può avere come fusilli = pasta,
ceci = legumi, sangria = vino. Non basarti solo ed esclusivamente sul nome esatto,
poichè, ad esempio, pasta è diverso da pasta sfoglia.

Rispondi SEMPRE chiamando una funzione quando possibile."""
    
    def cerca_prodotto(self, nome_prodotto: str, supermercato: str = None) -> Dict[str, Any]:
        """Cerca un prodotto nel database"""
        logger.info(f"Cerco prodotto: {nome_prodotto} (supermercato: {supermercato or 'tutti'})")
        
        # Espandi sinonimi e varianti
        varianti = self._espandi_sinonimi(nome_prodotto)
        
        # Cerca con tutte le varianti
        all_results = []
        for variante in varianti:
            results = self.db.search_products(variante, supermercato, limit=10)
            all_results.extend(results)
        
        # Rimuovi duplicati (stesso nome+prezzo)
        unique_results = []
        seen = set()
        for r in all_results:
            key = (r['nome'], r['prezzo'], r['supermercato'])
            if key not in seen:
                seen.add(key)
                unique_results.append(r)
        
        # Ordina per prezzo e limita
        unique_results.sort(key=lambda x: x['prezzo'])
        unique_results = unique_results[:5]
        
        if not unique_results:
            return {
                "trovati": 0,
                "messaggio": f"Nessun prodotto trovato per '{nome_prodotto}'"
            }
        
        return {
            "trovati": len(unique_results),
            "prodotti": unique_results
        }
    
    def _espandi_sinonimi(self, parola: str) -> List[str]:
        """Espande una parola con sinonimi e varianti"""
        sinonimi_map = {
            'uova': ['uov', 'uovo'],
            'uovo': ['uov'],
            'legumi': ['cec', 'fagioli', 'lenticch', 'piselli', 'legume'],
            'pane': ['pane', 'panino', 'panini'],
            'pasta': ['pasta', 'spaghetti', 'penne', 'fusilli'],
            'olio': ['olio'],
            'pomodoro': ['pomodor'],
            'pomodori': ['pomodor'],
            'birra': ['birra', 'beer'],
            'salumi': ['salame', 'salami', 'prosciutto', 'speck', 'bresaola'],
        }
        
        parola_lower = parola.lower()
        if parola_lower in sinonimi_map:
            return sinonimi_map[parola_lower]
        else:
            return [parola_lower]
    
    def trova_offerte(self, min_sconto: float = 5.0) -> Dict[str, Any]:
        """Trova prodotti in offerta"""
        logger.info(f"Cerco offerte (min sconto: {min_sconto}%)")
        
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
            "ranking": results,
            "lista_richiesta": lista_spesa  # Aggiungi per formattazione
        }
    
    def storico_prezzi(self, nome_prodotto: str) -> Dict[str, Any]:
        """Ottiene lo storico prezzi di un prodotto"""
        logger.info(f"Recupero storico prezzi: {nome_prodotto}")
        
        history = self.db.get_price_history(nome_prodotto)
        
        if not history:
            return {
                "trovati": 0,
                "messaggio": f"Nessuno storico per '{nome_prodotto}'"
            }
        
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
        Usa pattern matching intelligente + LLM per formattare le risposte
        
        Args:
            user_message: Messaggio dell'utente
        
        Returns:
            Risposta del LLM
        """
        logger.info(f"User: {user_message}")
        
        user_lower = user_message.lower()
        
        # Pattern matching per identificare l'intento
        result = None
        
        # 1. Offerte
        if any(word in user_lower for word in ['offerta', 'offerte', 'sconto', 'sconti', 'promozione']):
            # Estrai sconto minimo se specificato
            import re
            sconto_match = re.search(r'(\d+)%', user_message)
            min_sconto = float(sconto_match.group(1)) if sconto_match else 5.0
            
            result = self.trova_offerte(min_sconto=min_sconto)
            intent = "offerte"
        
        # 2. Storico prezzi
        elif any(word in user_lower for word in ['storico', 'storia', 'cambiato', 'variazione']):
            # Estrai nome prodotto
            prodotto = self._extract_product_name(user_message)
            if prodotto:
                result = self.storico_prezzi(prodotto)
                intent = "storico"
        
        # 3. Query multiple ("mostrami anche X, Y e Z")
        elif any(word in user_lower for word in ['anche', 'inoltre', 'mostrami', 'cerca']):
            prodotti = self._extract_product_list(user_message)
            if len(prodotti) > 1:
                # Prova prima ottimizzazione
                result = self.ottimizza_spesa(prodotti)
                # Se non trova nulla, mostra i singoli prodotti
                if result.get('supermercati_migliori', 0) == 0:
                    result = self._cerca_multipli(prodotti)
                    intent = "cerca_multi"
                else:
                    intent = "ottimizza"
            elif prodotti:
                # Un solo prodotto → cerca
                result = self.cerca_prodotto(prodotti[0])
                intent = "cerca"
        
        # 4. Ottimizza spesa (lista di prodotti)
        elif any(word in user_lower for word in ['comprare', 'voglio', 'lista', 'spesa', 'risparmiare']):
            # Estrai lista prodotti
            prodotti = self._extract_product_list(user_message)
            if len(prodotti) >= 2:  # Almeno 2 prodotti → ottimizza
                result = self.ottimizza_spesa(prodotti)
                # Se non trova nulla, mostra i singoli prodotti
                if result.get('supermercati_migliori', 0) == 0:
                    result = self._cerca_multipli(prodotti)
                    intent = "cerca_multi"
                else:
                    intent = "ottimizza"
            elif prodotti:
                # Un solo prodotto → cerca
                result = self.cerca_prodotto(prodotti[0])
                intent = "cerca"
        
        # 5. Cerca prodotto (default)
        else:
            prodotto = self._extract_product_name(user_message)
            if prodotto:
                result = self.cerca_prodotto(prodotto)
                intent = "cerca"
        
        if not result:
            return "Mi dispiace, non ho capito la domanda. Prova a chiedere: 'Dove trovo il latte?' o 'Quali sono le offerte?'"
        
        # Usa LLM per formattare la risposta
        return self._format_response(user_message, result, intent)
    
    def _extract_product_name(self, text: str) -> Optional[str]:
        """Estrae il nome del prodotto dalla domanda"""
        text_lower = text.lower()
        
        # Lista prodotti comuni (ampliata)
        keywords = ['latte', 'pane', 'pasta', 'olio', 'acqua', 'pomodoro', 'pomodori', 
                   'mozzarella', 'prosciutto', 'yogurt', 'biscotti', 'biscotto', 
                   'zucchero', 'farina', 'riso', 'burro', 'formaggio', 'caffè', 
                   'the', 'tè', 'succo', 'cereali', 'uova', 'uovo', 'legumi', 'legume',
                   'ceci', 'fagioli', 'lenticchie', 'piselli', 'salame', 'salumi',
                   'insalata', 'pollo', 'carne', 'pesce', 'tonno', 'verdura', 'verdure',
                   'birra', 'vino', 'bibita', 'bevanda']
        
        # Cerca keyword
        for keyword in keywords:
            if keyword in text_lower:
                return keyword
        
        # Pattern: "trovo il/la PRODOTTO"
        pattern = r'(?:trovo|cerco|costa|prezzo di|prezzo del|storico del) (?:il |la |i |le )?(\w+)'
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _extract_product_list(self, text: str) -> List[str]:
        """Estrae una lista di prodotti dalla domanda"""
        products = []
        text_lower = text.lower()
        
        # Lista prodotti completa (allineata con _extract_product_name)
        keywords = ['latte', 'pane', 'pasta', 'olio', 'acqua', 'pomodoro', 'pomodori',
                   'mozzarella', 'prosciutto', 'yogurt', 'biscotti', 'biscotto',
                   'zucchero', 'farina', 'riso', 'burro', 'formaggio', 'caffè',
                   'the', 'tè', 'succo', 'cereali', 'uova', 'uovo', 'legumi', 'legume',
                   'ceci', 'fagioli', 'lenticchie', 'piselli', 'salame', 'salumi',
                   'insalata', 'pollo', 'carne', 'pesce', 'tonno', 'verdura', 'verdure',
                   'birra', 'vino', 'bibita', 'bevanda']
        
        # Trova tutte le keyword presenti
        for keyword in keywords:
            if keyword in text_lower:
                products.append(keyword)
        
        return list(set(products))  # Rimuovi duplicati
    
    def _cerca_multipli(self, prodotti: List[str]) -> Dict[str, Any]:
        """Cerca più prodotti contemporaneamente"""
        risultati = {}
        for prodotto in prodotti:
            risultati[prodotto] = self.cerca_prodotto(prodotto)
        return {'prodotti_cercati': prodotti, 'risultati': risultati}
    
    def _format_response(self, question: str, data: Dict, intent: str) -> str:
        """Formatta la risposta (usa fallback manuale, LLM troppo piccolo)"""
        # FunctionGemma:270m è troppo piccolo per formattare bene
        # Usa sempre formattazione manuale
        return self._format_manual(data, intent)
    
    def _format_manual(self, data: Dict, intent: str) -> str:
        """Formattazione manuale dei risultati (fallback senza LLM)"""
        if intent == "cerca":
            if data['trovati'] == 0:
                return data['messaggio']
            
            result = f"Ho trovato {data['trovati']} prodotti:\n\n"
            for i, p in enumerate(data['prodotti'][:5], 1):
                marca = f" ({p['marca']})" if p.get('marca') else ""
                unita = f" - {p['unita_misura']}" if p.get('unita_misura') else ""
                result += f"{i}. {p['nome']}{marca}{unita}\n"
                result += f"   €{p['prezzo']:.2f} @ {p['supermercato']}\n\n"
            return result
        
        elif intent == "cerca_multi":
            result = ""
            for prodotto, dati in data['risultati'].items():
                result += f"\n🔍 {prodotto.upper()}:\n"
                if dati['trovati'] == 0:
                    result += f"   ❌ Nessun prodotto trovato\n"
                else:
                    for i, p in enumerate(dati['prodotti'][:3], 1):
                        marca = f" ({p['marca']})" if p.get('marca') else ""
                        unita = f" - {p['unita_misura']}" if p.get('unita_misura') else ""
                        result += f"   {i}. {p['nome']}{marca}{unita} → €{p['prezzo']:.2f}\n"
            return result
        
        elif intent == "offerte":
            if data['offerte_trovate'] == 0:
                return "Non ho trovato offerte attive al momento."
            
            result = f"🎉 {data['offerte_trovate']} offerte trovate:\n\n"
            for i, o in enumerate(data['offerte'][:5], 1):
                result += f"{i}. {o['nome']} ({o['marca']})\n"
                result += f"   Da €{o['prezzo_prima']:.2f} → €{o['prezzo_ora']:.2f} (-{o['sconto']:.0f}%)\n"
                result += f"   📍 {o['supermercato']}\n\n"
            return result
        
        elif intent == "ottimizza":
            if data['supermercati_migliori'] == 0:
                return "Non ho trovato supermercati con questi prodotti."
            
            prodotti_list = ", ".join(data.get('lista_richiesta', []))
            result = f"💡 Per: {prodotti_list}\n\n"
            result += "🛒 Supermercati migliori:\n\n"
            
            for i, s in enumerate(data['ranking'][:3], 1):
                result += f"{i}. {s['supermercato']}\n"
                result += f"   💰 Totale: €{s['prezzo_totale']:.2f}\n"
                result += f"   ✅ Disponibilità: {s['disponibilita']}\n"
                
                # Mostra dettaglio prodotti
                if s.get('prodotti'):
                    result += f"\n   📋 Prodotti:\n"
                    for prod in s['prodotti']:
                        nome = prod['prodotto'][:40]  # Tronca nomi lunghi
                        marca = f" ({prod['marca']})" if prod.get('marca') else ""
                        result += f"      • {prod['item']:12} → {nome}{marca}\n"
                        result += f"        {'':14}  €{prod['prezzo']:.2f}\n"
                
                result += "\n"
            
            return result
        
        elif intent == "storico":
            if data['rilevazioni'] == 0:
                return data['messaggio']
            
            result = "📊 Storico prezzi:\n\n"
            for i, h in enumerate(data['storico'][:5], 1):
                result += f"{i}. {h['data']}: €{h['prezzo']:.2f} @ {h['supermercato']}\n"
            return result
        
        return str(data)
    
    def _execute_function(self, func_name: str, params_str: str) -> Any:
        """Esegue una funzione specificata dal LLM"""
        try:
            # Parsea i parametri (parsing semplificato)
            params = {}
            
            # Estrai parametri semplici (key="value" o key=value)
            param_matches = re.findall(r'(\w+)\s*=\s*(["\']?)([^,\)]+)\2', params_str)
            for key, _, value in param_matches:
                # Converti tipi
                if value.lower() == 'true':
                    params[key] = True
                elif value.lower() == 'false':
                    params[key] = False
                elif value.replace('.', '').isdigit():
                    params[key] = float(value) if '.' in value else int(value)
                else:
                    # Rimuovi virgolette se presenti
                    params[key] = value.strip('"\'')
            
            # Gestisci liste (caso speciale per OTTIMIZZA_SPESA)
            list_match = re.search(r'lista_prodotti\s*=\s*\[(.*?)\]', params_str)
            if list_match:
                items_str = list_match.group(1)
                items = [item.strip().strip('"\'') for item in items_str.split(',')]
                params['lista_prodotti'] = items
            
            logger.debug(f"Parametri parsati: {params}")
            
            # Mappa funzioni
            if func_name == 'cerca_prodotto':
                return self.cerca_prodotto(
                    params.get('nome_prodotto', ''),
                    params.get('supermercato')
                )
            elif func_name == 'trova_offerte':
                return self.trova_offerte(params.get('min_sconto', 5.0))
            elif func_name == 'ottimizza_spesa':
                return self.ottimizza_spesa(params.get('lista_prodotti', []))
            elif func_name == 'storico_prezzi':
                return self.storico_prezzi(params.get('nome_prodotto', ''))
            else:
                return {"error": f"Funzione sconosciuta: {func_name}"}
        
        except Exception as e:
            logger.error(f"Errore esecuzione funzione: {e}", exc_info=True)
            return {"error": str(e)}
    
    def close(self):
        """Chiude le connessioni"""
        self.optimizer.close()


# Script standalone per chat interattiva
def main():
    """Modalità chat interattiva"""
    print("🤖 Assistente Spesa con LLM")
    print("=" * 60)
    print("Comandi disponibili:")
    print("  - Fai domande sui prodotti (es. 'Dove trovo il latte?')")
    print("  - Ottimizza la spesa (es. 'Cerca latte, pane e pasta')")
    print("  - 'esci' per terminare")
    print("=" * 60)
    print()
    
    # Disabilita log INFO per output più pulito
    import logging
    for logger_name in ['__main__', 'src.llm_interface', 'src.db', 'src.shopping_optimizer', 
                        'db', 'llm_interface', 'shopping_optimizer']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    try:
        assistant = GemmaShoppingAssistant()
        
        while True:
            user_input = input("\n👤 Tu: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['esci', 'exit', 'quit', 'q']:
                print("\n👋 Arrivederci!")
                break
            
            print("\n🤖 Assistente: ", end="", flush=True)
            response = assistant.chat(user_input)
            print(response)
        
        assistant.close()
    
    except ImportError:
        print("\n❌ Ollama non installato!")
        print("Installa con: pip install ollama")
        print("E assicurati che Ollama sia in esecuzione: ollama serve")
    except KeyboardInterrupt:
        print("\n\n👋 Arrivederci!")
    except Exception as e:
        logger.error(f"Errore: {e}", exc_info=True)
        print(f"\n❌ Errore: {e}")


if __name__ == "__main__":
    main()
