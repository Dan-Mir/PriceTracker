"""
Sistema di logging centralizzato per il supermarket parser
"""
import logging
import os
from logging.handlers import RotatingFileHandler

try:
    from config import LOG_DIR, LOG_FILE, LOG_LEVEL, LOG_FORMAT, LOG_MAX_BYTES, LOG_BACKUP_COUNT
except ImportError:
    from src.config import LOG_DIR, LOG_FILE, LOG_LEVEL, LOG_FORMAT, LOG_MAX_BYTES, LOG_BACKUP_COUNT


def setup_logger(name: str, log_file: str = None, level: str = None) -> logging.Logger:
    """
    Configura e restituisce un logger con rotazione file
    
    Args:
        name: Nome del logger (solitamente __name__)
        log_file: Nome file di log (opzionale, default da config)
        level: Livello di logging (opzionale, default da config)
    
    Returns:
        Logger configurato
    """
    # Crea directory log se non esiste
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    # Configura logger
    logger = logging.getLogger(name)
    log_level = getattr(logging, level or LOG_LEVEL)
    logger.setLevel(log_level)
    
    # Evita duplicazione handler se logger già configurato
    if logger.handlers:
        return logger
    
    # Handler per file con rotazione
    log_path = os.path.join(LOG_DIR, log_file or LOG_FILE)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    # Handler per console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Formattazione
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Aggiungi handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Ottiene un logger già configurato o ne crea uno nuovo
    
    Args:
        name: Nome del logger
    
    Returns:
        Logger configurato
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
