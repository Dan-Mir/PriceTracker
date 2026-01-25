"""
Utilities per gestione errori, retry e rate limiting
"""
import time
import random
from functools import wraps
from typing import Callable, Any, Tuple, Type
from config import MAX_RETRIES, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX
from logger import get_logger

logger = get_logger(__name__)


def retry_on_exception(
    max_retries: int = MAX_RETRIES,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    delay: float = 1.0,
    backoff: float = 2.0,
    logger_instance = None
) -> Callable:
    """
    Decorator per retry automatico in caso di eccezione
    
    Args:
        max_retries: Numero massimo di tentativi
        exceptions: Tuple di eccezioni da gestire
        delay: Delay iniziale tra tentativi (secondi)
        backoff: Fattore moltiplicativo per delay (exponential backoff)
        logger_instance: Logger da usare (opzionale)
    
    Returns:
        Decorated function
    
    Example:
        @retry_on_exception(max_retries=3, exceptions=(TimeoutError,))
        def fragile_function():
            # Codice che potrebbe fallire
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            log = logger_instance or logger
            current_delay = delay
            
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        log.error(f"{func.__name__} fallito dopo {max_retries} tentativi: {e}")
                        raise
                    
                    log.warning(f"{func.__name__} tentativo {attempt}/{max_retries} fallito: {e}. Riprovo tra {current_delay:.1f}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator


def rate_limit(min_delay: float = REQUEST_DELAY_MIN, max_delay: float = REQUEST_DELAY_MAX) -> Callable:
    """
    Decorator per rate limiting con delay casuale
    
    Args:
        min_delay: Delay minimo tra chiamate (secondi)
        max_delay: Delay massimo tra chiamate (secondi)
    
    Returns:
        Decorated function
    
    Example:
        @rate_limit(min_delay=2, max_delay=5)
        def fetch_page():
            # Codice di scraping
            pass
    """
    def decorator(func: Callable) -> Callable:
        last_call = [0.0]  # Usa lista per mutabilità in closure
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Calcola tempo trascorso dall'ultima chiamata
            elapsed = time.time() - last_call[0]
            
            # Calcola delay necessario
            required_delay = random.uniform(min_delay, max_delay)
            
            if elapsed < required_delay:
                sleep_time = required_delay - elapsed
                logger.debug(f"Rate limit: attendo {sleep_time:.2f}s prima di {func.__name__}")
                time.sleep(sleep_time)
            
            # Aggiorna timestamp ultima chiamata
            last_call[0] = time.time()
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def timeout_handler(timeout_seconds: int, default_return: Any = None) -> Callable:
    """
    Decorator per gestire timeout (versione semplificata senza threading)
    
    Args:
        timeout_seconds: Timeout in secondi
        default_return: Valore da restituire in caso di timeout
    
    Returns:
        Decorated function
    
    Note:
        Questa è una versione semplificata. Per timeout reali usare threading/multiprocessing
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                if elapsed > timeout_seconds:
                    logger.warning(f"{func.__name__} ha impiegato {elapsed:.1f}s (timeout={timeout_seconds}s)")
                
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                if elapsed > timeout_seconds:
                    logger.error(f"{func.__name__} timeout dopo {elapsed:.1f}s: {e}")
                    return default_return
                raise
        
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default=None, log_errors=True, **kwargs) -> Any:
    """
    Esegue una funzione in modo sicuro, ritornando un valore default in caso di errore
    
    Args:
        func: Funzione da eseguire
        *args: Argomenti posizionali per la funzione
        default: Valore di default da restituire in caso di errore
        log_errors: Se True, logga gli errori
        **kwargs: Argomenti keyword per la funzione
    
    Returns:
        Risultato della funzione o valore default
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error(f"Errore in {func.__name__}: {e}")
        return default


class RateLimiter:
    """
    Rate limiter con stato per limitare chiamate nel tempo
    """
    
    def __init__(self, min_delay: float = REQUEST_DELAY_MIN, max_delay: float = REQUEST_DELAY_MAX):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_call = 0.0
    
    def wait(self):
        """Attende il tempo necessario per rispettare il rate limit"""
        elapsed = time.time() - self.last_call
        required_delay = random.uniform(self.min_delay, self.max_delay)
        
        if elapsed < required_delay:
            sleep_time = required_delay - elapsed
            logger.debug(f"Rate limiter: attendo {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_call = time.time()
    
    def reset(self):
        """Reset del rate limiter"""
        self.last_call = 0.0
