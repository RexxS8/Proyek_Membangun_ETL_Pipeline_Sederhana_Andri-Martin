import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_page_content(url):
    """Fetch HTML content from a given URL with comprehensive error handling."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out for URL: {url}")
        return None
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred for {url}: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Error fetching {url}: {req_err}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return None

def parse_product_details(product_div):
    """Extract product details from a product div element with error handling."""
    try:
        if not product_div:
            raise ValueError("Empty product_div provided")
            
        title_element = product_div.find('h3', class_='product-title')
        if not title_element:
            raise ValueError("Title element not found")
        title = title_element.text.strip()
        
        # Price extraction with multiple fallbacks
        price = None
        try:
            price_container = product_div.find('div', class_='price-container')
            if price_container:
                price_span = price_container.find('span', class_='price')
                if price_span:
                    price = price_span.text.strip().replace('$', '')
        except Exception as e:
            logger.warning(f"Error extracting price: {e}")
        
        # Rating extraction
        rating = None
        try:
            rating_text = product_div.find('p', string=lambda text: text and 'Rating:' in text)
            if rating_text:
                rating = rating_text.text.strip().split('⭐')[-1].strip().split('/')[0].strip()
        except Exception as e:
            logger.warning(f"Error extracting rating: {e}")
        
        # Colors extraction
        colors = None
        try:
            colors_text = product_div.find('p', string=lambda text: text and 'Colors' in text)
            colors = colors_text.text.strip().split()[0] if colors_text else None
        except Exception as e:
            logger.warning(f"Error extracting colors: {e}")
        
        # Size extraction
        size = None
        try:
            size_text = product_div.find('p', string=lambda text: text and 'Size:' in text)
            size = size_text.text.replace('Size:', '').strip() if size_text else None
        except Exception as e:
            logger.warning(f"Error extracting size: {e}")
        
        # Gender extraction
        gender = None
        try:
            gender_text = product_div.find('p', string=lambda text: text and 'Gender:' in text)
            gender = gender_text.text.replace('Gender:', '').strip() if gender_text else None
        except Exception as e:
            logger.warning(f"Error extracting gender: {e}")
        
        return {
            'Title': title,
            'Price': price,
            'Rating': rating,
            'Colors': colors,
            'Size': size,
            'Gender': gender
        }
        
    except Exception as e:
        logger.error(f"Error parsing product details: {e}")
        return None

def scrape_products(base_url, max_pages=50):
    """Scrape products from all pages of the website with error handling."""
    products = []
    timestamp = datetime.now().isoformat()
    current_url = base_url
    pages_scraped = 0
    
    try:
        while current_url and pages_scraped < max_pages:
            logger.info(f"Scraping page {pages_scraped + 1}...")
            
            html_content = fetch_page_content(current_url)
            if not html_content:
                logger.warning(f"Failed to fetch content from {current_url}")
                break
                
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract products from current page
                product_divs = soup.find_all('div', class_='product-details')
                if not product_divs:
                    logger.warning(f"No products found on page {pages_scraped + 1}")
                
                for div in product_divs:
                    product = parse_product_details(div)
                    if product:
                        product['Timestamp'] = timestamp
                        products.append(product)
                
                # Find next page link
                next_link = soup.find('li', class_='page-item next')
                if next_link and next_link.find('a'):
                    current_url = urljoin(base_url, next_link.find('a')['href'])
                else:
                    current_url = None
                
                pages_scraped += 1
                time.sleep(1)  # Be polite with delay between requests
                
            except Exception as page_err:
                logger.error(f"Error processing page {pages_scraped + 1}: {page_err}")
                current_url = None
        
    except Exception as e:
        logger.error(f"Fatal error in scrape_products: {e}")
    
    return products