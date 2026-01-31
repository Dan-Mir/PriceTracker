"""
Sistema di espansione keyword usando le categorie del database
"""
from typing import List, Dict, Set
from src.logger import get_logger

logger = get_logger(__name__)


class KeywordExpander:
    """
    Espande le keyword generiche usando le categorie del database
    """
    
    # Mappatura keyword → categorie database
    KEYWORD_TO_CATEGORIES = {
        # Pasta e cereali
        "pasta": ["Pasta", "Pasta fresca, sughi e piatti pronti", "Gastronomia, salumi e formaggi > Pasta fresca e ripiena"],
        
        # Latticini
        "latte": ["Latte Uova E Burro", "Latticini e uova > Latte, burro e uova", "Latticini"],
        "formaggio": ["Altri Formaggi", "I Nostri Formaggi Selezionati", "Parmigiano Reggiano E Grana Padano",
                     "Gastronomia, salumi e formaggi > Formaggi al taglio", "Gastronomia, salumi e formaggi > Formaggi confezionati",
                     "Crescenza Ricotta Robiola"],
        "mozzarella": ["Mozzarella", "Altri Formaggi"],
        "yogurt": ["Yogurt E Dessert", "Latticini e uova > Yogurt e dessert"],
        "burro": ["Latte Uova E Burro", "Latticini e uova > Latte, burro e uova"],
        "uova": ["Latte Uova E Burro", "Latticini e uova > Latte, burro e uova"],
        
        # Carne e pesce
        "carne": ["Carne", "Carne e pesce > Carne", "Bovino E Vitello", "Pollame E Agnello", "Suino"],
        "pesce": ["Carne e pesce > Pesce", "Mare E Acqua Dolce", "Salmone Affumicato", "Molluschi", "Pesce e salmone affumicato"],
        "salumi": ["Salumi Confezionati", "I Nostri Salumi Selezionati", "Gastronomia, salumi e formaggi > Salumi", "Salumi Interi E Tranci"],
        
        # Frutta e verdura
        "frutta": ["Frutta Fresca", "Frutta e verdura > Frutta", "Frutta Sciroppata", "Frutta Secca", "Altra Frutta"],
        "verdura": ["Verdura Fresca", "Frutta e verdura > Verdura", "Altre Verdure", "Verdure Pronte", "Verdura Cotta"],
        "pomodori": ["Pomodori E Pomodorini"],
        "insalata": ["Insalata Lavata", "Insalate E Radicchi", "Insalate Pronte Minestre E Zuppe"],
        "patate": ["Patate E Funghi"],
        
        # Pane e prodotti da forno
        "pane": ["Pane e pasticceria > Pane", "Pane, sostitutivi e snack salati", "Pane e pasticceria > Pane a fette e piadine"],
        "biscotti": ["Biscotti E Merendine", "Fette Biscottate"],
        "dolci": ["Colazione e dolci", "Pasticceria E Torte", "Pane e pasticceria > Pasticceria"],
        
        # Bevande
        "acqua": ["Acqua, bibite e succhi"],
        "bibite": ["Acqua, bibite e succhi"],
        "succhi": ["Acqua, bibite e succhi"],
        "vino": ["Vini", "Vini, birra e liquori"],
        "birra": ["Birra", "Vini, birra e liquori"],
        "caffè": ["Caffe E Solubili", "Caffè, tea e zucchero"],
        "te": ["Tea E Infusi", "Caffè, tea e zucchero"],
        
        # Altri prodotti
        "riso": ["Riso", "Pasta, riso e farine", "Farro E Cereali"],
        "farina": ["Farina Pure E Preparati", "Pasta, riso e farine"],
        "olio": ["Semi E Condimenti"],
        "zucchero": ["Zucchero E Dolcificanti", "Caffè, tea e zucchero"],
        "marmellata": ["Marmellate Miele E Spalmabili"],
        "cioccolato": ["Cioccolata"],
        "conserve": ["Conserve"],
        "surgelati": ["Surgelati e gelati"],
    }
    
    # Sinonimi per migliorare il matching
    SYNONYMS = {
        "pasta": ["fusilli", "penne", "spaghetti", "rigatoni", "farfalle", "linguine", "orecchiette", "tortellini"],
        "latte": ["parzialmente scremato", "intero", "scremato", "senza lattosio"],
        "formaggio": ["parmigiano", "grana", "pecorino", "gorgonzola", "taleggio"],
        "carne": ["manzo", "vitello", "maiale", "pollo", "tacchino", "agnello"],
        "pesce": ["salmone", "tonno", "merluzzo", "orata", "branzino"],
    }
    
    def expand_keyword(self, keyword: str) -> Dict[str, any]:
        """
        Espande una keyword in categorie e sinonimi
        
        Args:
            keyword: Keyword da espandere (es. "pasta")
            
        Returns:
            Dict con:
            - categories: Lista categorie correlate
            - synonyms: Lista sinonimi
            - original: Keyword originale
        """
        keyword_lower = keyword.lower().strip()
        
        categories = self.KEYWORD_TO_CATEGORIES.get(keyword_lower, [])
        synonyms = self.SYNONYMS.get(keyword_lower, [])
        
        if categories:
            logger.info(f"Keyword '{keyword}' → {len(categories)} categorie, {len(synonyms)} sinonimi")
        
        return {
            "original": keyword,
            "categories": categories,
            "synonyms": synonyms
        }
    
    def get_search_terms(self, keyword: str) -> List[str]:
        """
        Genera tutti i termini di ricerca per una keyword
        
        Args:
            keyword: Keyword originale
            
        Returns:
            Lista di termini da cercare
        """
        expansion = self.expand_keyword(keyword)
        terms = [expansion["original"]]
        terms.extend(expansion["synonyms"])
        
        return list(set(terms))  # Rimuovi duplicati
