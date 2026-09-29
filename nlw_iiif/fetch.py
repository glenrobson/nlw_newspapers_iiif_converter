import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "nlw-newspapers-iiif-converter/0.1"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
# Minimum seconds between requests to newspapers.library.wales, to be polite to the server.
REQUEST_DELAY = 1.0

_last_request = 0.0


def cache_path(url: str) -> Path:
    """Map a URL to a cache file, e.g. /browse/3036868 -> cache/browse/3036868.html.

    Query strings are kept in the filename so paginated URLs don't overwrite each
    other, e.g. /browse/3036868/list?page=2 -> cache/browse/3036868/list_page_2.html.
    """
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p] or ["index"]
    if parsed.query:
        parts[-1] += "_" + re.sub(r"[^A-Za-z0-9]+", "_", parsed.query)
    return CACHE_DIR.joinpath(*parts[:-1], f"{parts[-1]}.html")


def wait_for_rate_limit() -> None:
    """Sleep until at least REQUEST_DELAY seconds have passed since the last request."""
    global _last_request
    wait = _last_request + REQUEST_DELAY - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()


def get_soup(url: str, timeout: int = 30) -> BeautifulSoup:
    """Fetch a URL (or read it from the cache) and return it parsed as BeautifulSoup."""
    path = cache_path(url)
    if path.exists():
        print (f'Reading from cache: {url}')
        html = path.read_text(encoding="utf-8")
    else:
        wait_for_rate_limit()
        print (f'Fetching: {url}')
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        response.raise_for_status()
        html = response.text
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    return BeautifulSoup(html, "html.parser")
