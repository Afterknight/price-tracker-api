# 1. Import necessary libraries
from fastapi.responses import RedirectResponse 
import re
from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
import re 

# 2. Create a FastAPI app instance
app = FastAPI(
    title="Product Price Tracker API",
    description="An API to scrape product details like price and title from e-commerce sites.",
    version="1.0.0",
)

# 3. Define the main endpoint
@app.get("/v1/product-details")
async def get_product_details(url: str):
    """
    Scrapes a given product URL to extract its title, price, and availability.
    Currently optimized for Amazon.com.
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required.")

    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 

        # 5. Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # 6. Extract product details
        product_title_element = soup.select_one('span#productTitle')
        product_title = product_title_element.get_text().strip() if product_title_element else "Title not found"

        # Find the product price
        # Amazon often splits the price into whole and fractional parts
        price_whole_element = soup.select_one('span.a-price-whole')
        price_fraction_element = soup.select_one('span.a-price-fraction')
        
        if price_whole_element and price_fraction_element:
            price_str = f"{price_whole_element.get_text().strip()}{price_fraction_element.get_text().strip()}"
            # Clean the string to remove currency symbols and commas, then convert to float
            price_cleaned = re.sub(r'[^\d.]', '', price_str)
            price = float(price_cleaned) if price_cleaned else 0.0
        else:
            price = 0.0 # Or some other default/error indicator

        # Find availability
        availability_element = soup.select_one('div#availability span.a-size-medium')
        availability = availability_element.get_text().strip() if availability_element else "Availability not found"

        # Find currency
        currency_element = soup.select_one('span.a-price-symbol')
        currency = currency_element.get_text().strip() if currency_element else "USD"

        # 7. Structure and return the final JSON response
        return {
            "success": True,
            "product_url": url,
            "product_title": product_title,
            "price": price,
            "currency": currency,
            "availability": availability
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch URL: {e}")
    except Exception as e:
        # A catch-all for parsing errors or other unexpected issues
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# A simple root endpoint to REDIRECT to the documentation
@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")