
import sys
import os
import time
import logging
from concurrent.futures import ProcessPoolExecutor
import math

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.castoro.castoro_parser import CastoroParser
from src.castoro.castoro_all_urls import CASTORO_SUBCATEGORY_URLS
from src import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Process %(process)d] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/parallel_scraping.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_category_chunk(urls_chunk, chunk_id):
    """
    Process a chunk of URLs in a separate process
    """
    logger.info(f"Starting chunk {chunk_id} with {len(urls_chunk)} categories")
    
    # Initialize parser for this process
    parser = CastoroParser(headless=True)
    # Override categories
    parser.SUBCATEGORIES = urls_chunk
    
    total_saved = 0
    
    try:
        parser._setup_driver()
        parser.driver.get(parser.BASE_URL)
        time.sleep(config.PAGE_LOAD_DELAY)
        parser._remove_cookie_banner()
        
        for i, subcategory_url in enumerate(urls_chunk, 1):
            category_name = subcategory_url.split('/')[-1].replace('-', ' ').title()
            logger.info(f"[Chunk {chunk_id}] Processing {i}/{len(urls_chunk)}: {category_name}")
            
            try:
                products = parser._scrape_category_by_url(subcategory_url)
                if products:
                    parser._save_products(products)
                    total_saved += len(products)
            except Exception as e:
                logger.error(f"[Chunk {chunk_id}] Error in {category_name}: {e}")
            
            # Small delay between categories within the same process
            time.sleep(config.CATEGORY_DELAY)
            
    except Exception as e:
        logger.error(f"[Chunk {chunk_id}] Fatal error: {e}")
    finally:
        parser.close()
        
    logger.info(f"Finished chunk {chunk_id}. Total saved: {total_saved}")
    return total_saved

def main():
    # Number of parallel processes
    # CAUTION: Each process spawns a Chrome instance. 
    # Don't set too high or you'll run out of RAM/CPU.
    MAX_WORKERS = 4 
    
    all_urls = CASTORO_SUBCATEGORY_URLS
    total_urls = len(all_urls)
    chunk_size = math.ceil(total_urls / MAX_WORKERS)
    
    chunks = [all_urls[i:i + chunk_size] for i in range(0, total_urls, chunk_size)]
    
    logger.info(f"Starting parallel scraping with {MAX_WORKERS} workers")
    logger.info(f"Total categories: {total_urls}")
    logger.info(f"Chunk size: ~{chunk_size}")
    
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for i, chunk in enumerate(chunks):
            futures.append(executor.submit(process_category_chunk, chunk, i+1))
            
        total_products = 0
        for future in futures:
            try:
                total_products += future.result()
            except Exception as e:
                logger.error(f"Worker failed: {e}")
                
    duration = time.time() - start_time
    logger.info(f"Parallel scraping completed in {duration:.2f} seconds")
    logger.info(f"Total products saved: {total_products}")

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    main()
