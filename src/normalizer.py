"""
Modulo per la normalizzazione e matching intelligente dei prodotti
"""
import re
from typing import List, Tuple, Optional, Dict
from difflib import SequenceMatcher

try:
    from config import (
        FUZZY_MATCH_THRESHOLD, 
        PRODUCT_SYNONYMS, 
        UNIT_CONVERSIONS,
        UNIT_PATTERNS
    )
    from logger import get_logger
except ImportError:
    from src.config import (
        FUZZY_MATCH_THRESHOLD, 
        PRODUCT_SYNONYMS, 
        UNIT_CONVERSIONS,
        UNIT_PATTERNS
    )
    from src.logger import get_logger

logger = get_logger(__name__)


class ProductNormalizer:
    """Classe per normalizzare e confrontare prodotti"""
    
    def __init__(self):
        self.synonyms = PRODUCT_SYNONYMS
        self.unit_conversions = UNIT_CONVERSIONS
        self.unit_patterns = UNIT_PATTERNS
    
    def normalize_text(self, text: str) -> str:
        """
        Normalizza il testo di un prodotto
        
        Args:
            text: Testo da normalizzare
        
        Returns:
            Testo normalizzato (lowercase, senza punteggiatura)
        """
        if not text:
            return ""
        
        # Lowercase
        normalized = text.lower().strip()
        
        # Rimuovi punteggiatura eccessiva
        normalized = re.sub(r'[^\w\s.,]', '', normalized)
        
        # Normalizza spazi multipli
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def extract_unit(self, text: str) -> Optional[str]:
        """
        Estrae l'unità di misura dal testo
        
        Args:
            text: Testo del prodotto
        
        Returns:
            Unità di misura estratta o None
        """
        text_lower = text.lower()
        
        # Cerca pattern di peso
        for pattern_type, pattern in self.unit_patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def normalize_unit(self, unit: str) -> str:
        """
        Normalizza unità di misura (es. "1kg" -> "1 kg")
        
        Args:
            unit: Unità da normalizzare
        
        Returns:
            Unità normalizzata
        """
        if not unit:
            return ""
        
        # Rimuovi spazi
        normalized = unit.lower().replace(" ", "")
        
        # Aggiungi spazio tra numero e unità
        normalized = re.sub(r'(\d+)([a-z]+)', r'\1 \2', normalized)
        
        # Normalizza virgole in punti
        normalized = normalized.replace(',', '.')
        
        return normalized.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizza il testo in parole significative
        
        Args:
            text: Testo da tokenizzare
        
        Returns:
            Lista di token
        """
        normalized = self.normalize_text(text)
        
        # Rimuovi numeri isolati e parole di 1-2 caratteri
        tokens = [
            word for word in normalized.split() 
            if len(word) > 2 and not word.isdigit()
        ]
        
        return tokens
    
    def expand_synonyms(self, word: str) -> List[str]:
        """
        Espande una parola con i suoi sinonimi
        
        Args:
            word: Parola da espandere
        
        Returns:
            Lista contenente la parola originale e sinonimi
        """
        word_lower = word.lower()
        
        # Cerca nei sinonimi
        for main_word, synonyms in self.synonyms.items():
            if word_lower == main_word or word_lower in synonyms:
                return [main_word] + synonyms
        
        return [word_lower]
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """
        Calcola il punteggio di similarità tra due testi (0-100)
        
        Args:
            text1: Primo testo
            text2: Secondo testo
        
        Returns:
            Punteggio di similarità (0-100)
        """
        # Normalizza i testi
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        # Sequence Matcher di Python (Ratcliff-Obershelp)
        ratio = SequenceMatcher(None, norm1, norm2).ratio()
        
        return ratio * 100
    
    def token_similarity(self, text1: str, text2: str) -> float:
        """
        Calcola similarità basata sui token condivisi (Jaccard similarity)
        
        Args:
            text1: Primo testo
            text2: Secondo testo
        
        Returns:
            Punteggio di similarità (0-100)
        """
        tokens1 = set(self.tokenize(text1))
        tokens2 = set(self.tokenize(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Jaccard similarity
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        jaccard = len(intersection) / len(union)
        
        return jaccard * 100
    
    def fuzzy_match(self, product1: str, product2: str, threshold: float = None) -> bool:
        """
        Verifica se due prodotti sono simili
        
        Args:
            product1: Nome primo prodotto
            product2: Nome secondo prodotto
            threshold: Soglia di similarità (default da config)
        
        Returns:
            True se i prodotti sono simili
        """
        threshold = threshold or FUZZY_MATCH_THRESHOLD
        
        # Calcola entrambe le metriche
        seq_score = self.similarity_score(product1, product2)
        token_score = self.token_similarity(product1, product2)
        
        # Media ponderata (60% sequence, 40% token)
        combined_score = (seq_score * 0.6) + (token_score * 0.4)
        
        logger.debug(f"Fuzzy match '{product1}' vs '{product2}': seq={seq_score:.1f}, token={token_score:.1f}, combined={combined_score:.1f}")
        
        return combined_score >= threshold
    
    def find_best_match(self, query: str, candidates: List[str], threshold: float = None) -> Optional[Tuple[str, float]]:
        """
        Trova il miglior match da una lista di candidati
        
        Args:
            query: Testo da cercare
            candidates: Lista di testi candidati
            threshold: Soglia minima di similarità
        
        Returns:
            Tupla (miglior_candidato, score) o None se nessun match
        """
        threshold = threshold or FUZZY_MATCH_THRESHOLD
        
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            seq_score = self.similarity_score(query, candidate)
            token_score = self.token_similarity(query, candidate)
            combined_score = (seq_score * 0.6) + (token_score * 0.4)
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = candidate
        
        if best_score >= threshold:
            logger.debug(f"Best match for '{query}': '{best_match}' (score: {best_score:.1f})")
            return (best_match, best_score)
        
        return None
    
    def extract_brand_from_text(self, text: str, product_name: str) -> Optional[str]:
        """
        Tenta di estrarre la marca dal testo del prodotto
        
        Args:
            text: Testo completo della card prodotto
            product_name: Nome del prodotto già estratto
        
        Returns:
            Marca estratta o None
        """
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Rimuovi la linea del nome prodotto
        lines = [l for l in lines if l != product_name]
        
        # Cerca parole in MAIUSCOLO (spesso marche)
        for line in lines:
            # Salta prezzi e unità
            if '€' in line or any(c.isdigit() for c in line):
                continue
            
            # Se è tutto maiuscolo e > 2 caratteri, probabilmente è una marca
            if line.isupper() and len(line) > 2:
                return line.title()  # Capitalizza
            
            # Cerca keyword che indicano marche
            if any(keyword in line.lower() for keyword in ['s.p.a', 'srl', '®', '™']):
                return line.strip()
        
        # Prendi la prima linea valida come fallback (se esiste)
        valid_lines = [
            l for l in lines 
            if len(l) > 2 
            and '€' not in l 
            and not any(word in l.lower() for word in ['aggiungi', 'carrello', 'offerta'])
        ]
        
        if valid_lines:
            # Se la prima linea è breve (<15 caratteri), è probabilmente una marca
            if len(valid_lines[0]) < 15:
                return valid_lines[0].strip()
        
        return None


# Istanza globale per uso rapido
normalizer = ProductNormalizer()


# Funzioni helper per accesso rapido
def fuzzy_match(product1: str, product2: str, threshold: float = None) -> bool:
    """Verifica se due prodotti sono simili"""
    return normalizer.fuzzy_match(product1, product2, threshold)


def extract_unit(text: str) -> Optional[str]:
    """Estrae unità di misura dal testo"""
    return normalizer.extract_unit(text)


def normalize_product_name(name: str) -> str:
    """Normalizza nome prodotto"""
    return normalizer.normalize_text(name)


def find_best_match(query: str, candidates: List[str], threshold: float = None) -> Optional[Tuple[str, float]]:
    """Trova miglior match da lista candidati"""
    return normalizer.find_best_match(query, candidates, threshold)
