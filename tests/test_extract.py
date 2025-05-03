import pytest
from unittest.mock import patch, Mock
from utils.extract import fetch_page_content, parse_product_details, scrape_products
from bs4 import BeautifulSoup
from datetime import datetime

def test_fetch_page_content_success():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>Test content</html>"
        mock_get.return_value = mock_response
        
        result = fetch_page_content("https://fashion-studio.dicoding.dev")
        assert result == "<html>Test content</html>"

def test_fetch_page_content_failure():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        
        result = fetch_page_content("https://fashion-studio.dicoding.dev")
        assert result is None

def test_parse_product_details():
    html = """
    <div class="product-details">
        <h3 class="product-title">Test Product</h3>
        <div class="price-container"><span class="price">$100.00</span></div>
        <p style="font-size: 14px; color: #777;">Rating: ⭐ 4.5 / 5</p>
        <p style="font-size: 14px; color: #777;">3 Colors</p>
        <p style="font-size: 14px; color: #777;">Size: M</p>
        <p style="font-size: 14px; color: #777;">Gender: Women</p>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    product_div = soup.find('div', class_='product-details')
    
    result = parse_product_details(product_div)
    assert result['Title'] == "Test Product"
    assert result['Price'] == "100.00"
    assert result['Rating'] == "4.5"
    assert result['Colors'] == "3"
    assert result['Size'] == "M"
    assert result['Gender'] == "Women"

@patch('utils.extract.fetch_page_content')
def test_scrape_products(mock_fetch):
    mock_fetch.return_value = """
    <html>
        <body>
            <div class="product-details">
                <h3 class="product-title">Test Product</h3>
                <div class="price-container"><span class="price">$100.00</span></div>
                <p style="font-size: 14px; color: #777;">Rating: ⭐ 4.5 / 5</p>
                <p style="font-size: 14px; color: #777;">3 Colors</p>
                <p style="font-size: 14px; color: #777;">Size: M</p>
                <p style="font-size: 14px; color: #777;">Gender: Women</p>
            </div>
            <li class="page-item next"><a class='page-link' href='/page2'>Next</a></li>
        </body>
    </html>
    """
    
    results = scrape_products("https://fashion-studio.dicoding.dev", max_pages=1)
    assert len(results) == 1
    assert results[0]['Title'] == "Test Product"
    assert 'Timestamp' in results[0]  # Pastikan timestamp ada