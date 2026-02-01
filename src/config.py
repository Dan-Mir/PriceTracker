"""
Configurazione centralizzata per il supermarket parser
"""
import os
from dotenv import load_dotenv

load_dotenv("../.env")

# ==================== DATABASE ====================
DATABASE_NAME = os.path.join(os.path.dirname(__file__), "prezzi.db")
DATABASE_BACKUP_DIR = "backups"

# ==================== SCRAPING ====================
# Timeout e delay
SELENIUM_TIMEOUT = 25  # secondi per WebDriverWait
PAGE_LOAD_DELAY = 3    # secondi di attesa dopo caricamento pagina (ridotto)
SCROLL_DELAY = 1       # secondi di attesa dopo scroll (ridotto)
LOGIN_DELAY = 8        # secondi di attesa dopo login
CATEGORY_DELAY = 2     # secondi tra una categoria e l'altra (ridotto)
NEXT_PAGE_DELAY = 2    # secondi tra una pagina e l'altra (ridotto)

# Rate limiting
REQUEST_DELAY_MIN = 1  # delay minimo tra richieste (secondi)
REQUEST_DELAY_MAX = 3  # delay massimo tra richieste (secondi)

# Limiti
MAX_ITERATIONS = 500   # aumentato per coprire tutte le categorie
MAX_PAGES_PER_CATEGORY = 60  # massimo numero di pagine per categoria
MAX_RETRIES = 3        # numero tentativi in caso di errore

# ==================== EUROSPIN ====================
EUROSPIN_URL = "https://laspesaonline.eurospin.it"
EUROSPIN_COOKIE_FILE = "cookies.pkl"
EUROSPIN_EMAIL = os.getenv("EUROSPIN_EMAIL", "")

# Blacklist URL (parole da ignorare nei link)
URL_BLACKLIST = [
    "faq", "assistenza", "contatti", "privacy", "cookie", "policy", 
    "login", "registrati", "volantino", "negozi", "store", "chi-siamo", 
    "lavora-con-noi", "servizio-clienti", "informativa", "condizioni", 
    "ritiro", "consegna", "pagamenti", "home", "aiuto", "scrivici",
    "social", "facebook", "instagram", "app", "dove-siamo", "javascript",
    "carrello", "checkout", "profile", "account", "ordini"
]

# Selettori CSS comuni per prezzi
PRICE_SELECTORS = [
    ".price", 
    ".prezzo", 
    "[class*='price']", 
    "[class*='prezzo']",
    ".product-price",
    ".sale-price"
]

# ==================== CHROME DRIVER ====================
CHROME_OPTIONS = [
    '--headless',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--window-size=1920,1080',
    '--disable-blink-features=AutomationControlled',
    '--disable-extensions',
    '--disable-gpu',
    '--blink-settings=imagesEnabled=false' # Disabilita immagini per velocità
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
# ==================== LLM ====================
LLM_MODEL = "functiongemma:270m"  # Modello Ollama per function calling
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 512
# ==================== LOGGING ====================
LOG_DIR = "logs"
LOG_FILE = "scraper.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# ==================== PARSING ====================
# Parole chiave per identificare unità di misura
UNIT_PATTERNS = {
    'weight': r'\d+[.,]?\d*\s*(g|gr|grammi?|kg|kilogrammi?|etto|hg)\b',
    'volume': r'\d+[.,]?\d*\s*(ml|millilitri?|cl|centilitri?|l|lt|litri?)\b',
    'quantity': r'\d+\s*(pz|pezzi?|pz\.|conf|confezioni?|x)\b'
}

# Parole da ignorare durante il parsing
PARSING_IGNORE_WORDS = [
    "aggiungi", "al kg", "al pz", "al litro", "carrello", 
    "totale", "riepilogo", "disponibile", "esaurito",
    "nuovo", "offerta", "promo", "sconto"
]

# Parole chiave per identificare marche
BRAND_KEYWORDS = [
    "s.p.a", "spa", "s.r.l", "srl", "s.n.c", "snc",
    "®", "™", "©"
]

# ==================== NORMALIZZAZIONE PRODOTTI ====================
# Soglia di similarità per fuzzy matching (0-100)
FUZZY_MATCH_THRESHOLD = 80

# Sinonimi comuni per normalizzazione
PRODUCT_SYNONYMS = {
    "latte": ["milk", "bevanda lattea"],
    "pane": ["bread", "filone", "baguette"],
    "pasta": ["spaghetti", "penne", "fusilli", "rigatoni"],
    "acqua": ["water", "h2o", "minerale"],
    "olio": ["oil", "extravergine", "evo"],
    "caffè": ["coffee", "caffe"],
    "the": ["tea", "tè", "tisana"],
    "biscotti": ["cookies", "frollini"]
}

# Varianti unità di misura equivalenti
UNIT_CONVERSIONS = {
    "1 kg": ["1000 g", "1000g", "1kg", "1000 gr"],
    "1 l": ["1000 ml", "1000ml", "1l", "1lt", "1 litro"],
    "500 g": ["0.5 kg", "500g", "0,5 kg"],
    "500 ml": ["0.5 l", "500ml", "0,5 l"]
}

# ==================== SHOPPING OPTIMIZER ====================
# Pesi per l'algoritmo di ranking
RANKING_WEIGHT_PRICE = 0.7  # 70% peso al prezzo
RANKING_WEIGHT_AVAILABILITY = 0.3  # 30% peso alla disponibilità

# Numero di supermercati da restituire
TOP_SUPERMARKETS_COUNT = 3

# ==================== DEBUG ====================
SCREENSHOT_DIR = "screenshots"
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
SAVE_SCREENSHOTS = os.getenv("SAVE_SCREENSHOTS", "False").lower() == "true"
