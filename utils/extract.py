import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_page_content(url):
    """Fetch HTML content from a given URL with error handling."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_product_details(product_div):
    """Extract product details from a product div element."""
    try:
        title = product_div.find('h3', class_='product-title').text.strip()
        
        # Handle price extraction
        price_container = product_div.find('div', class_='price-container')
        if price_container:
            price_span = price_container.find('span', class_='price')
            if price_span:
                price = price_span.text.strip().replace('$', '')
            else:
                price = None
        else:
            price = None
        
        # Handle rating extraction
        rating_text = product_div.find('p', string=lambda text: text and 'Rating:' in text)
        if rating_text:
            rating = rating_text.text.strip().split('⭐')[-1].strip().split('/')[0].strip()
        else:
            rating = None
        
        # Handle colors extraction
        colors_text = product_div.find('p', string=lambda text: text and 'Colors' in text)
        colors = colors_text.text.strip().split()[0] if colors_text else None
        
        # Handle size extraction
        size_text = product_div.find('p', string=lambda text: text and 'Size:' in text)
        size = size_text.text.replace('Size:', '').strip() if size_text else None
        
        # Handle gender extraction
        gender_text = product_div.find('p', string=lambda text: text and 'Gender:' in text)
        gender = gender_text.text.replace('Gender:', '').strip() if gender_text else None
        
        return {
            'Title': title,
            'Price': price,
            'Rating': rating,
            'Colors': colors,
            'Size': size,
            'Gender': gender
        }
    except Exception as e:
        print(f"Error parsing product: {e}")
        return None

def scrape_products(base_url, max_pages=50):
    """Scrape products from all pages of the website using pagination."""
    products = []
    timestamp = datetime.now().isoformat()
    current_url = base_url
    pages_scraped = 0
    
    while current_url and pages_scraped < max_pages:
        print(f"Scraping page {pages_scraped + 1}...")
        
        html_content = fetch_page_content(current_url)
        if not html_content:
            break
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract products from current page
        product_divs = soup.find_all('div', class_='product-details')
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
            current_url = None  # No more pages
        
        pages_scraped += 1
        time.sleep(1)  # Be polite with delay between requests
    
    return products