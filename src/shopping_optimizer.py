"""
Shopping List Optimizer - Trova i supermercati più convenienti per una lista della spesa
"""
from typing import List, Dict, Optional, Tuple

try:
    from db import PriceDatabase
    from normalizer import ProductNormalizer
    from logger import get_logger
    import config
except ImportError:
    from src.db import PriceDatabase
    from src.normalizer import ProductNormalizer
    from src.logger import get_logger
    from src import config

logger = get_logger(__name__)


class ShoppingOptimizer:
    """Ottimizza la spesa trovando i supermercati più economici"""
    
    def __init__(self, db: PriceDatabase = None):
        self.db = db or PriceDatabase()
        self.normalizer = ProductNormalizer()
        self.own_db = db is None  # Se abbiamo creato il DB, dobbiamo chiuderlo
    
    def find_best_supermarkets(self, shopping_list: List[str], top_n: int = 3) -> List[Dict]:
        """
        Trova i migliori supermercati per una lista della spesa
        
        Args:
            shopping_list: Lista di prodotti da cercare (es. ['latte', 'pane', 'pasta'])
            top_n: Numero di supermercati da restituire (default: 3)
        
        Returns:
            Lista di dict con ranking supermercati:
            [
                {
                    'supermercato': 'Eurospin',
                    'prezzo_totale': 8.50,
                    'disponibilita': '3/3',
                    'prodotti': [
                        {'item': 'latte', 'prodotto': 'Latte Intero 1L', 'prezzo': 1.29, ...},
                        ...
                    ],
                    'score': 0.95
                },
                ...
            ]
        """
        logger.info(f"Ottimizzazione spesa per {len(shopping_list)} prodotti")
        
        # Ottieni tutti i supermercati
        supermarkets = self.db.get_all_supermarkets()
        
        if not supermarkets:
            logger.warning("Nessun supermercato trovato nel database")
            return []
        
        results = []
        
        for supermarket in supermarkets:
            logger.debug(f"Analisi supermercato: {supermarket}")
            
            total_price = 0.0
            matched_products = []
            items_found = 0
            
            for item in shopping_list:
                # 1. Espandi sinonimi per migliore ricerca
                varianti = self._espandi_sinonimi(item)
                
                # 2. Cerca prodotti candidati nel supermercato (tutte le varianti)
                all_candidates = []
                for variante in varianti:
                    candidates = self.db.search_products(variante, supermarket, limit=10)
                    all_candidates.extend(candidates)
                
                # Rimuovi duplicati
                unique_candidates = []
                seen = set()
                for c in all_candidates:
                    key = (c['nome'], c['prezzo'])
                    if key not in seen:
                        seen.add(key)
                        unique_candidates.append(c)
                
                # 3. Trova il miglior match usando fuzzy matching
                best_match = self._find_best_product(item, unique_candidates)
                
                if best_match:
                    total_price += best_match['prezzo']
                    items_found += 1
                    matched_products.append({
                        'item': item,
                        'prodotto': best_match['nome'],
                        'marca': best_match['marca'],
                        'prezzo': best_match['prezzo'],
                        'unita_misura': best_match['unita_misura']
                    })
                    logger.debug(f"Match: '{item}' → '{best_match['nome']}' (€{best_match['prezzo']:.2f})")
                else:
                    logger.debug(f"Nessun match per '{item}' in {supermarket}")
            
            # 3. Calcola score combinato (disponibilità + prezzo)
            if items_found > 0:
                availability_score = items_found / len(shopping_list)
                # Normalizza il prezzo (più basso = score più alto)
                price_score = 1 / (total_price + 1)
                
                # Score combinato con pesi configurabili
                combined_score = (
                    config.RANKING_WEIGHT_PRICE * price_score +
                    config.RANKING_WEIGHT_AVAILABILITY * availability_score
                )
                
                results.append({
                    'supermercato': supermarket,
                    'prezzo_totale': round(total_price, 2),
                    'disponibilita': f'{items_found}/{len(shopping_list)}',
                    'items_trovati': items_found,
                    'items_mancanti': len(shopping_list) - items_found,
                    'prodotti': matched_products,
                    'score': round(combined_score, 4)
                })
                
                logger.info(f"{supermarket}: €{total_price:.2f}, {items_found}/{len(shopping_list)} prodotti, score={combined_score:.4f}")
        
        # 4. Ordina per score (migliore prima)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_n]
    
    def _find_best_product(self, query: str, candidates: List[Dict]) -> Optional[Dict]:
        """
        Trova il prodotto migliore tra i candidati usando fuzzy matching
        
        Args:
            query: Termine di ricerca dall'utente
            candidates: Lista di prodotti candidati dal DB
        
        Returns:
            Migliore prodotto match o None
        """
        if not candidates:
            return None
        
        # Se c'è un solo candidato, ritornalo
        if len(candidates) == 1:
            return candidates[0]
        
        # Estrai i nomi dei prodotti candidati
        candidate_names = [c['nome'] for c in candidates]
        
        # Usa normalizer per trovare il miglior match
        best_match = self.normalizer.find_best_match(query, candidate_names, threshold=70)
        
        if best_match:
            best_name, score = best_match
            logger.debug(f"Fuzzy match: '{query}' → '{best_name}' (score: {score:.1f})")
            # Ritorna il prodotto completo corrispondente
            for candidate in candidates:
                if candidate['nome'] == best_name:
                    return candidate
        
        # Fallback: ritorna il primo candidato (più economico, ordinato dal DB)
        logger.debug(f"Fallback match per '{query}': {candidates[0]['nome']}")
        return candidates[0]
    
    def _espandi_sinonimi(self, parola: str) -> list:
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
    
    def print_results(self, results: List[Dict], shopping_list: List[str]):
        """
        Stampa i risultati in formato leggibile
        
        Args:
            results: Risultati da find_best_supermarkets()
            shopping_list: Lista spesa originale
        """
        if not results:
            print("\n❌ Nessun supermercato trovato con questi prodotti")
            return
        
        print(f"\n🛒 MIGLIORI SUPERMERCATI PER LA TUA SPESA")
        print(f"📋 Lista: {', '.join(shopping_list)}\n")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['supermercato'].upper()}")
            print(f"   💰 Totale: €{result['prezzo_totale']:.2f}")
            print(f"   ✅ Disponibilità: {result['disponibilita']}")
            
            if result['items_mancanti'] > 0:
                print(f"   ⚠️  {result['items_mancanti']} prodotto/i non trovato/i")
            
            print(f"   📊 Score: {result['score']:.4f}")
            print(f"\n   Prodotti trovati:")
            
            for prod in result['prodotti']:
                marca_str = f" [{prod['marca']}]" if prod['marca'] else ""
                unita_str = f" ({prod['unita_misura']})" if prod['unita_misura'] else ""
                print(f"     • {prod['item']:15} → {prod['prodotto']}{marca_str}{unita_str}")
                print(f"       {'':17}   €{prod['prezzo']:.2f}")
        
        print("\n" + "=" * 80)
    
    def close(self):
        """Chiude il database se creato internamente"""
        if self.own_db and self.db:
            self.db.close()
