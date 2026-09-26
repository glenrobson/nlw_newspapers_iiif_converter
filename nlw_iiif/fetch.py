from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "nlw-newspapers-iiif-converter/0.1"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"


def cache_path(url: str) -> Path:
    """Map a URL to a cache file, e.g. /browse/3036868 -> cache/browse/3036868.html."""
    parts = [p for p in urlparse(url).path.split("/") if p] or ["index"]
    return CACHE_DIR.joinpath(*parts).with_suffix(".html")


def get_soup(url: str, timeout: int = 30) -> BeautifulSoup:
    """Fetch a URL (or read it from the cache) and return it parsed as BeautifulSoup."""
    path = cache_path(url)
    if path.exists():
        html = path.read_text(encoding="utf-8")
    else:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        response.raise_for_status()
        html = response.text
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    return BeautifulSoup(html, "html.parser")
