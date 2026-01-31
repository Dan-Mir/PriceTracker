"""
Ottimizzatore ibrido: FunctionGemma (locale) + Gemini API (cloud)

Architettura:
1. FunctionGemma estrae keywords e fa query al DB
2. Gemini API analizza i risultati e sceglie i prodotti più appropriati
"""
import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.logger import get_logger
from src.db import PriceDatabase
from src.llm_interface import GemmaShoppingAssistant
from src.keyword_expander import KeywordExpander

load_dotenv()
logger = get_logger(__name__)


class HybridShoppingOptimizer:
    """
    Ottimizzatore ibrido che combina:
    - FunctionGemma (locale): estrazione keywords + function call
    - Gemini API (cloud): ragionamento semantico e selezione intelligente
    """
    
    def __init__(self, gemini_model: str = "gemini-2.0-flash"):
        """
        Inizializza l'ottimizzatore ibrido
        
        Args:
            gemini_model: Modello Gemini da usare (default: gemini-2.0-flash)
        """
        self.db = PriceDatabase()
        self.expander = KeywordExpander()
        
        # FunctionGemma per function calling locale
        try:
            self.local_llm = GemmaShoppingAssistant()
            logger.info(f"FunctionGemma inizializzato: {self.local_llm.model}")
        except Exception as e:
            logger.error(f"Errore inizializzazione FunctionGemma: {e}")
            raise
        
        # Gemini API per ragionamento semantico
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY non trovata nel .env")
        
        self.client = genai.Client(api_key=api_key)
        self.gemini_model = gemini_model
        logger.info(f"Gemini API inizializzato: {gemini_model}")
    
    def optimize_shopping_list(self, shopping_list: List[str]) -> Dict[str, Any]:
        """
        Ottimizza una lista della spesa usando l'approccio ibrido
        
        Args:
            shopping_list: Lista di prodotti richiesti
            
        Returns:
            Dizionario con risultati ottimizzati e reasoning
        """
        logger.info(f"Ottimizzazione lista: {shopping_list}")
        
        # STEP 1: FunctionGemma estrae keywords
        keywords = self._extract_keywords(shopping_list)
        logger.info(f"Keywords estratte: {keywords}")
        
        # STEP 2: Query database per ogni keyword (con espansione categorie)
        all_results = {}
        for product_name, kw in zip(shopping_list, keywords):
            # Espandi keyword in categorie
            expansion = self.expander.expand_keyword(kw)
            categories = expansion['categories']
            
            # Ricerca avanzata: nome + categorie
            results = self.db.search_products_enhanced(
                query=kw,
                categories=categories if categories else None,
                limit=20
            )
            
            if results:
                all_results[product_name] = results
                logger.info(f"'{product_name}' → trovati {len(results)} match (categorie: {len(categories)})")
            else:
                all_results[product_name] = []
                logger.warning(f"'{product_name}' → nessun match")
        
        # STEP 3: Gemini API fa il reasoning semantico
        optimized = self._semantic_selection(shopping_list, all_results)
        
        return optimized
    
    def _extract_keywords(self, products: List[str]) -> List[str]:
        """
        Usa FunctionGemma per estrarre keywords dai prodotti
        
        Args:
            products: Lista prodotti originali
            
        Returns:
            Lista keywords normalizzate
        """
        # Usa il normalizzatore già integrato in GemmaShoppingAssistant
        keywords = []
        for product in products:
            # Normalizzazione base (lowercase, rimozione caratteri speciali)
            kw = product.lower().strip()
            # Estrai prima parola significativa
            words = kw.split()
            main_word = words[0] if words else kw
            keywords.append(main_word)
        
        return keywords
    
    def _semantic_selection(self, products: List[str], db_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Usa Gemini API per selezionare i prodotti più appropriati semanticamente
        
        Args:
            products: Lista prodotti richiesti dall'utente
            db_results: Dizionario con risultati del database per ogni prodotto
            
        Returns:
            Dizionario con selezione ottimizzata e reasoning
        """
        # Costruisci prompt per Gemini
        prompt = self._build_gemini_prompt(products, db_results)
        
        logger.info("Invio richiesta a Gemini API...")
        
        try:
            response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=prompt
            )
            logger.info("Risposta ricevuta da Gemini")
            
            # Parsing della risposta JSON
            result = self._parse_gemini_response(response.text)
            
            return result
            
        except Exception as e:
            logger.error(f"Errore Gemini API: {e}")
            # Fallback: usa primo risultato per ogni prodotto
            return self._fallback_selection(products, db_results)
    
    def _build_gemini_prompt(self, products: List[str], db_results: Dict[str, List[Dict]]) -> str:
        """
        Costruisce il prompt per Gemini con i risultati del database
        """
        prompt = """Sei un assistente esperto per l'ottimizzazione della spesa.

L'utente ha richiesto questa lista della spesa:
{products}

Il database ha trovato questi prodotti potenziali:

{db_results}

COMPITO:
1. Per ogni prodotto richiesto, seleziona il match più appropriato dal database
2. Considera il CONTESTO SEMANTICO (es. "Pasta Barilla" = pasta alimentare secca, NON pasta sfoglia)
3. Preferisci prodotti con nome/marca che matchano meglio
4. Escludi prodotti fuori contesto (es. "yogurt al caffè" se richiesto "caffè")
5. Calcola quale supermercato conviene di più per la spesa totale
6. Per ogni prodotto restituisci la top 3 dei risultati

Rispondi SOLO con JSON in questo formato (senza markdown, commenti o testo extra):
{{
  "selections": [
    {{
      "requested": "Pasta Barilla",
      "options": [
        {{
          "nome": "Penne Barilla",
          "prezzo": 1.29,
          "supermercato": "Eurospin",
          "reasoning": "Pasta secca Barilla"
        }},
        {{
          "nome": "Fusilli Barilla",
          "prezzo": 1.35,
          "supermercato": "Castoro",
          "reasoning": "Alternativa pasta Barilla"
        }},
        {{
          "nome": "Spaghetti Barilla",
          "prezzo": 1.19,
          "supermercato": "Eurospin",
          "reasoning": "Opzione economica"
        }}
      ]
    }}
  ],
  "best_store": "Eurospin",
  "total_price": 15.50,
  "coverage": "9/10"
}}

IMPORTANTE:
- NO markdown code blocks (```json)
- NO commenti nel JSON
- NO apostrofi o virgolette singole nei valori
- USA solo virgolette doppie
- COPIA il nome ESATTO dal database, NON aggiungere dettagli
- reasoning deve essere MAX 40 caratteri
- Se non trovi 3 opzioni, restituisci quelle disponibili
"""
        
        # Formatta lista prodotti
        products_str = "\n".join(f"- {p}" for p in products)
        
        # Formatta risultati database
        db_str = ""
        for product, results in db_results.items():
            db_str += f"\n### {product}:\n"
            if results:
                for i, r in enumerate(results[:10], 1):  # Max 10 per prodotto per dare più scelta
                    db_str += f"  {i}. {r['nome']} | €{r['prezzo']} | {r['supermercato']}\n"
            else:
                db_str += "  (Nessun risultato)\n"
        
        return prompt.format(products=products_str, db_results=db_str)
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parsing della risposta JSON di Gemini
        """
        # Rimuovi markdown se presente
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        try:
            result = json.loads(text)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Errore parsing JSON: {e}")
            logger.error(f"Risposta Gemini (primi 1000 char):\n{text[:1000]}")
            
            # Prova a salvare il JSON in un file per debug
            try:
                with open('/tmp/gemini_response_error.json', 'w') as f:
                    f.write(text)
                logger.info("Risposta salvata in /tmp/gemini_response_error.json")
            except:
                pass
            
            raise ValueError(f"JSON malformato da Gemini. Dettagli salvati in /tmp/gemini_response_error.json")
    
    def _fallback_selection(self, products: List[str], db_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Selezione fallback se Gemini API fallisce
        """
        selections = []
        total = 0.0
        count = 0
        
        for product in products:
            results = db_results.get(product, [])
            if results:
                # Top 3 opzioni
                options = []
                for r in results[:3]:
                    options.append({
                        "nome": r['nome'],
                        "prezzo": r['prezzo'],
                        "supermercato": r['supermercato'],
                        "reasoning": "Fallback automatico"
                    })
                
                selections.append({
                    "requested": product,
                    "options": options
                })
                
                # Usa il primo per calcolare totale
                total += results[0]['prezzo']
                count += 1
        
        return {
            "selections": selections,
            "best_store": "N/A",
            "total_price": round(total, 2),
            "coverage": f"{count}/{len(products)}"
        }
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """
        Formatta il risultato in modo leggibile con top 3 opzioni per prodotto
        """
        output = "\n" + "=" * 80 + "\n"
        output += "🛒 OTTIMIZZAZIONE SPESA CON GEMINI".center(80) + "\n"
        output += "=" * 80 + "\n\n"
        
        output += f"🏪 Supermercato consigliato: **{result['best_store']}**\n"
        output += f"💰 Totale (opzione migliore): **€{result['total_price']}**\n"
        output += f"✅ Copertura: **{result['coverage']}** prodotti trovati\n\n"
        
        output += "📋 PRODOTTI E ALTERNATIVE:\n"
        output += "-" * 80 + "\n"
        
        for selection in result['selections']:
            req = selection['requested']
            options = selection.get('options', [])
            
            output += f"\n🔹 **{req}**\n"
            
            if not options:
                output += "   ⚠️  Nessuna opzione trovata\n"
                continue
            
            # Mostra le 3 opzioni
            for i, opt in enumerate(options, 1):
                icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                output += f"\n   {icon} OPZIONE {i}\n"
                output += f"      📦 {opt['nome']}\n"
                output += f"      💵 €{opt['prezzo']} - {opt['supermercato']}\n"
                output += f"      💡 {opt['reasoning']}\n"
        
        output += "\n" + "=" * 80 + "\n"
        
        return output
        
        output += "\n" + "=" * 80 + "\n"
        
        return output


def main():
    """Test standalone"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python -m src.gemini_optimizer <file_lista_spesa.txt>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Leggi lista
    with open(file_path, 'r') as f:
        shopping_list = [line.strip() for line in f if line.strip()]
    
    print(f"📋 Lista della spesa ({len(shopping_list)} prodotti):")
    for i, item in enumerate(shopping_list, 1):
        print(f"  {i}. {item}")
    print()
    
    # Ottimizza
    optimizer = HybridShoppingOptimizer()
    result = optimizer.optimize_shopping_list(shopping_list)
    
    # Mostra risultato
    print(optimizer.format_result(result))


if __name__ == "__main__":
    main()
