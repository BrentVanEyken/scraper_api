import sys
import asyncio

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
import json

from . import scraper as s

app = FastAPI()


@app.get("/")

def read_root():
    return {"message": "Welcome to the FastAPI web scraper!"}

@app.get("/scrape/txt")
def scrape_content(url: str, xpath: str):
    """
    Scrape content from a website using the provided URL and XPath.
    
    Args:
        url (str): The URL of the website to scrape.
        xpath (str): The XPath to locate the desired content on the webpage.
    
    Returns:
        txt: The scraped content or an error message if scraping fails.
    """
    try:
        # Call the scraper function to get the content
        scraped_data = s.scrape_content_txt(url, xpath)
        if scraped_data:
            return {"scraped_data": scraped_data}
        else:
            return {"error": "No content found at the provided XPath."}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    
@app.get("/scrape/html")
def scrape_content(url: str, xpath: str):
    """
    Scrape content from a website using the provided URL and XPath.
    
    Args:
        url (str): The URL of the website to scrape.
        xpath (str): The XPath to locate the desired content on the webpage.
    
    Returns:
        html: The scraped content or an error message if scraping fails.
    """
    try:
        # Call the scraper function to get the content
        scraped_data = s.scrape_content_html(url, xpath)
        if scraped_data:
            return {"scraped_data": scraped_data}
        else:
            return {"error": "No content found at the provided XPath."}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
