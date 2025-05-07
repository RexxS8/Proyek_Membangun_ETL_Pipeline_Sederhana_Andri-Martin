import pytest
from unittest.mock import patch, Mock
from utils.extract import fetch_page_content, parse_product_details, scrape_products
from bs4 import BeautifulSoup
from datetime import datetime
import logging

# Test fetch_page_content
def test_fetch_page_content_success():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>Test content</html>"
        mock_get.return_value = mock_response
        
        result = fetch_page_content("http://test.com")
        assert result == "<html>Test content</html>"

def test_fetch_page_content_failure():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        result = fetch_page_content("http://test.com")
        assert result is None

# Test parse_product_details
def test_parse_product_details_valid():
    html = """
    <div class="product-details">
        <h3 class="product-title">Test Product</h3>
        <div class="price-container"><span class="price">$100.00</span></div>
        <p>Rating: ⭐ 4.5 / 5</p>
        <p>3 Colors</p>
        <p>Size: M</p>
        <p>Gender: Women</p>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    product_div = soup.find('div', class_='product-details')
    
    result = parse_product_details(product_div)
    assert result == {
        'Title': 'Test Product',
        'Price': '100.00',
        'Rating': '4.5',
        'Colors': '3',
        'Size': 'M',
        'Gender': 'Women'
    }

def test_parse_product_details_missing_fields():
    html = "<div class='product-details'><h3 class='product-title'>Test</h3></div>"
    soup = BeautifulSoup(html, 'html.parser')
    result = parse_product_details(soup.find('div'))
    assert result['Title'] == 'Test'
    assert result['Price'] is None
    assert result['Rating'] is None

# Test scrape_products
@patch('utils.extract.fetch_page_content')
def test_scrape_products_single_page(mock_fetch):
    mock_fetch.return_value = """
    <html>
        <body>
            <div class="product-details">
                <h3 class="product-title">Product 1</h3>
                <div class="price-container"><span class="price">$10.00</span></div>
            </div>
            <li class="page-item next"><a class='page-link' href='/page2'>Next</a></li>
        </body>
    </html>
    """
    results = scrape_products("http://test.com", max_pages=1)
    assert len(results) == 1
    assert results[0]['Title'] == "Product 1"

@patch('utils.extract.fetch_page_content')
def test_scrape_products_multiple_pages(mock_fetch):
    mock_fetch.side_effect = [
        """
        <html>
            <body>
                <div class="product-details"><h3 class="product-title">Page 1</h3></div>
                <li class="page-item next"><a class='page-link' href='/page2'>Next</a></li>
            </body>
        </html>
        """,
        """
        <html>
            <body>
                <div class="product-details"><h3 class="product-title">Page 2</h3></div>
            </body>
        </html>
        """
    ]
    results = scrape_products("http://test.com", max_pages=2)
    assert len(results) == 2
    assert results[0]['Title'] == "Page 1"
    assert results[1]['Title'] == "Page 2"

def test_scrape_products_error_handling(caplog):
    with patch('utils.extract.fetch_page_content', return_value=None):
        results = scrape_products("http://test.com")
        assert len(results) == 0
        assert "Failed to fetch content" in caplog.text