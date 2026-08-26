import time
from urllib.parse import urlparse

from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options


DEFAULT_TIMEOUT = 15


class ScraperError(Exception):
    """Base exception for scraper failures."""


class ScraperTimeoutError(ScraperError):
    """Raised when a page takes too long to load."""


class ScraperBlockedError(ScraperError):
    """Raised when the target site blocks the request."""


class ScraperStructureError(ScraperError):
    """Raised when the expected page structure is missing."""


def validate_url(url):
    """Validate that the supplied URL is an HTTP(S) URL."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL is required.")

    parsed = urlparse(url.strip())

    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("A valid HTTP or HTTPS URL is required.")

    return url.strip()


def create_driver():
    """Create a headless Chrome Selenium driver."""
    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(DEFAULT_TIMEOUT)
    driver.set_script_timeout(DEFAULT_TIMEOUT)

    return driver


def scrape_page(url, timeout=DEFAULT_TIMEOUT):
    """
    Open a webpage with Selenium and return basic page information.

    This intentionally provides a generic software-only scraper.
    Category-specific extraction can be added later without changing
    the API layer.
    """

    url = validate_url(url)

    if not isinstance(timeout, int) or timeout <= 0:
        raise ValueError("Timeout must be a positive integer.")

    driver = None

    try:
        driver = create_driver()

        driver.set_page_load_timeout(timeout)

        start_time = time.time()

        try:
            driver.get(url)

        except TimeoutException as exc:
            raise ScraperTimeoutError(
                "The webpage took too long to load."
            ) from exc

        elapsed = round(time.time() - start_time, 3)

        title = driver.title or ""

        page_source = driver.page_source or ""

        # Basic blocked-page detection.
        blocked_markers = [
            "access denied",
            "captcha",
            "verify you are human",
            "robot check",
            "request blocked",
        ]

        page_lower = page_source.lower()

        if any(marker in page_lower for marker in blocked_markers):
            raise ScraperBlockedError(
                "The target website appears to have blocked the scraper."
            )

        if not title and not page_source.strip():
            raise ScraperStructureError(
                "The webpage returned no usable content."
            )

        return {
            "url": url,
            "title": title,
            "page_length": len(page_source),
            "load_time_seconds": elapsed,
        }

    except ScraperError:
        raise

    except WebDriverException as exc:
        raise ScraperError(
            "Unable to access the webpage with Selenium."
        ) from exc

    finally:
        if driver is not None:
            driver.quit()