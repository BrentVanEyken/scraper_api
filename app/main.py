import sys
import asyncio
import os
import logging
from pathlib import Path
from typing import List, Optional, Callable
import re
from fastapi import Query

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings  # Updated import for BaseSettings
from lxml import html
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------------------
# Configuration & Logging
# ---------------------------

class Settings(BaseSettings):
    SCRAPER_API_TOKEN: str
    PLAYWRIGHT_TIMEOUT: int = 15000  # in milliseconds; adjust if needed

    class Config:
        env_file = str(Path(__file__).parent / ".env")

settings = Settings()
API_TOKEN = settings.SCRAPER_API_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ---------------------------
# FastAPI Application Setup
# ---------------------------
app = FastAPI(title="FastAPI Async Web Scraper")
browser = None  # Global variable for the playwright browser instance

@app.on_event("startup")
async def startup_event():
    global browser
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    # Store playwright instance in app state for proper cleanup
    app.state.playwright = playwright
    logger.info("Browser launched successfully on startup.")

@app.on_event("shutdown")
async def shutdown_event():
    global browser
    if browser:
        await browser.close()
    await app.state.playwright.stop()
    logger.info("Browser closed and playwright stopped on shutdown.")

# ---------------------------
# Scraping Utility Functions
# ---------------------------

async def get_page(url: str, wait_xpath: Optional[str] = None) -> html.HtmlElement:
    """
    Asynchronously fetches the page content using a shared browser instance.
    Waits for a specific element (by XPath) or for the network to be idle.
    """
    global browser
    try:
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, timeout=settings.PLAYWRIGHT_TIMEOUT)

        if wait_xpath:
            await page.wait_for_selector(f'xpath={wait_xpath}', timeout=settings.PLAYWRIGHT_TIMEOUT)
        else:
            await page.wait_for_load_state('networkidle', timeout=settings.PLAYWRIGHT_TIMEOUT)

        content = await page.content()
        tree = html.fromstring(content)
        await context.close()  # Clean up the context after use
        return tree
    except PlaywrightTimeoutError:
        logger.error(f"Timeout while fetching page: {url}")
        raise HTTPException(status_code=504, detail="Timeout while waiting for the element to appear.")
    except Exception as e:
        logger.error(f"Error fetching the page {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching the page: {e}")

def text_formatter(element) -> str:
    """Extracts and cleans text from an HTML element."""
    return element.text_content().strip()

def html_formatter(element) -> str:
    """Converts an HTML element to a pretty-printed HTML string."""
    return html.tostring(element, pretty_print=True, encoding="unicode")

async def scrape_content(url: str, xpath: str, formatter: Callable) -> Optional[str]:
    """
    Generalized scraping function that retrieves page content and applies a formatter.
    """
    tree = await get_page(url)
    results = tree.xpath(xpath)
    if results:
        combined = " ".join(formatter(element) for element in results if formatter(element))
        return combined if combined else None
    return None

async def scraper_scrape_content_txt(url: str, xpath: str) -> Optional[str]:
    """
    Scrapes and returns combined text content from elements matching the XPath.
    """
    return await scrape_content(url, xpath, text_formatter)

async def scraper_scrape_content_html(url: str, xpath: str) -> Optional[str]:
    """
    Scrapes and returns combined HTML content from elements matching the XPath.
    """
    return await scrape_content(url, xpath, html_formatter)


# ---------------------------
# Helper functions
# ---------------------------

def clean_scraped_chapter(raw_text: str) -> str:
    """
    Cleans scraped chapter content by removing JavaScript, ads, tracking tags,
    and unrelated content. Keeps only the actual story text.
    """
    import re

    # 1. Remove JavaScript ad and tracking blocks
    raw_text = re.sub(r"window\.pub.*?push\(\{.*?\}\);?", "", raw_text, flags=re.DOTALL)
    raw_text = re.sub(r"var\s+\w+\s*=\s*document\.getElementById\(.*?\);\s*", "", raw_text)
    raw_text = re.sub(r"\s*adx_id_\d+\.id\s*=.*?\n", "", raw_text)

    # 2. Remove promotional or upsell messages
    raw_text = re.sub(r"Enhance your reading experience.*?Remove Ads.*?\n", "", raw_text, flags=re.DOTALL)
    raw_text = re.sub(r"Remove Ads From \$\d+.*?\n", "", raw_text, flags=re.DOTALL)
    raw_text = re.sub(r"\$?\d+!", "", raw_text)  # Remove any lingering "$1!" kind of messages

    # 3. Remove repeated empty tag spaces and ad gaps
    raw_text = re.sub(r"\n\s*\n+", "\n\n", raw_text)  # Collapse multiple empty lines
    raw_text = re.sub(r"\n[ \t]+", "\n", raw_text)    # Clean up indentation on newlines
    raw_text = re.sub(r"[ \t]+\n", "\n", raw_text)

    # 4. Remove HTML entities or leftover Unicode symbols
    raw_text = re.sub(r"&[a-z]+;", "", raw_text)
    raw_text = re.sub(r"“|”", '"', raw_text)
    raw_text = re.sub(r"‘|’", "'", raw_text)

    # 5. Trim again
    cleaned_text = raw_text.strip()

    return cleaned_text


# ---------------------------
# Pydantic Models for Endpoints
# ---------------------------
class ScrapeTask(BaseModel):
    url: HttpUrl
    xpath: str
    data_type: Optional[str] = "TXT"  # "TXT" (default) or "HTML"

class ScrapeBatchRequest(BaseModel):
    tasks: List[ScrapeTask]

# ---------------------------
# API Endpoints
# ---------------------------
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI async web scraper!"}

@app.get("/scrape/txt")
async def scrape_txt(url: HttpUrl, xpath: str):
    """
    Endpoint to scrape text content from a provided URL using the specified XPath.
    """
    scraped_data = await scraper_scrape_content_txt(str(url), xpath)
    if scraped_data:
        return {"scraped_data": scraped_data}
    raise HTTPException(status_code=404, detail="No content found at the provided XPath.")

@app.get("/scrape/html")
async def scrape_html(url: HttpUrl, xpath: str):
    """
    Endpoint to scrape HTML content from a provided URL using the specified XPath.
    """
    scraped_data = await scraper_scrape_content_html(str(url), xpath)
    if scraped_data:
        return {"scraped_data": scraped_data}
    raise HTTPException(status_code=404, detail="No content found at the provided XPath.")

@app.post("/scrape/batch")
async def scrape_batch(request: ScrapeBatchRequest, authorization: Optional[str] = Header(None)):
    """
    Batch endpoint to process multiple scraping tasks concurrently.
    Expects an authorization header "Bearer {SCRAPER_API_TOKEN}".
    """
    if not authorization:
        raise HTTPException(status_code=403, detail="Authorization header missing.")
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=403, detail="Unauthorized.")

    async def process_task(task: ScrapeTask):
        try:
            data_type = task.data_type.upper()
            if data_type == "TXT":
                scraped_data = await scraper_scrape_content_txt(str(task.url), task.xpath)
            elif data_type == "HTML":
                scraped_data = await scraper_scrape_content_html(str(task.url), task.xpath)
            else:
                raise ValueError(f"Unsupported data_type '{task.data_type}'. Use 'TXT' or 'HTML'.")
            
            if scraped_data:
                return {
                    "url": task.url,
                    "xpath": task.xpath,
                    "scraped_data": scraped_data,
                    "status": "success"
                }
            return {
                "url": task.url,
                "xpath": task.xpath,
                "error": "No content found at the provided XPath.",
                "status": "failed"
            }
        except Exception as e:
            logger.error(f"Error processing task for URL {task.url}, XPath {task.xpath}: {e}")
            return {
                "url": task.url,
                "xpath": task.xpath,
                "error": str(e),
                "status": "failed"
            }

    results = await asyncio.gather(*(process_task(task) for task in request.tasks))
    return {"results": results}

@app.get("/scrape/cleaned-chapter")
async def scrape_cleaned_chapter(url: HttpUrl, xpath: str):
    """
    Scrapes text and returns a cleaned version of a chapter.
    """
    scraped_data = await scraper_scrape_content_txt(str(url), xpath)
    if scraped_data:
        cleaned_data = clean_scraped_chapter(scraped_data)
        return {"scraped_data": cleaned_data}
    raise HTTPException(status_code=404, detail="No content found at the provided XPath.")

@app.get("/scrape/cleaned-batch")
async def scrape_cleaned_batch(
    base_url: HttpUrl,
    xpath: str,
    chapter_start: int = Query(..., ge=1),
    chapter_end: int = Query(..., ge=1)
):
    """
    Batch scrapes and cleans chapters in the given range from a base URL.
    Example: base_url=https://example.com/novel, xpath=..., chapter_start=1, chapter_end=10
    Will scrape: https://example.com/novel/chapter-1 ... chapter-10
    """

    if chapter_end < chapter_start:
        raise HTTPException(status_code=400, detail="chapter_end must be >= chapter_start")

    async def process_chapter(chapter_number: int):
        chapter_url = f"{base_url}/chapter-{chapter_number}"
        try:
            raw_data = await scraper_scrape_content_txt(chapter_url, xpath)
            if raw_data:
                cleaned = clean_scraped_chapter(raw_data)
                return {
                    "chapter": chapter_number,
                    "url": chapter_url,
                    "scraped_data": cleaned,
                    "status": "success"
                }
            return {
                "chapter": chapter_number,
                "url": chapter_url,
                "error": "No content found at the XPath.",
                "status": "failed"
            }
        except Exception as e:
            logger.error(f"Error scraping chapter {chapter_number}: {e}")
            return {
                "chapter": chapter_number,
                "url": chapter_url,
                "error": str(e),
                "status": "failed"
            }

    tasks = [process_chapter(ch) for ch in range(chapter_start, chapter_end + 1)]
    results = await asyncio.gather(*tasks)
    return {"results": results}
