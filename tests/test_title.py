from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from nlw_iiif import fetch
from nlw_iiif.fetch import get_soup
from nlw_iiif.title import parse_title_page

FIXTURES = Path(__file__).parent / "fixtures"
TITLE_URL = "https://newspapers.library.wales/browse/3036868"
TITLE_HTML = (FIXTURES / "title.html").read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def empty_cache(tmp_path, monkeypatch):
    """Point the cache at a temp dir so tests never read or write the real cache."""
    monkeypatch.setattr(fetch, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(fetch, "REQUEST_DELAY", 0)


def mock_response(html: str) -> Mock:
    response = Mock()
    response.text = html
    response.raise_for_status.return_value = None
    return response


@patch("nlw_iiif.fetch.requests.get")
def test_parse_title(mock_get):
    mock_get.return_value = mock_response(TITLE_HTML)

    title = parse_title_page(get_soup(TITLE_URL))

    assert title["label"] == "The Aberystwith Observer"
    assert title["copyright"] == "UNKNOWN"
    assert title["frequency"] == "Weekly" 
    assert title["publisher"] == "Published in Aberystwyth by David Jenkins."
    assert title["dates"] == "1858 - 1910"
    assert title["summary"] == "A weekly English language newspaper, supportive of conservative politics, which circulated in Ceredigion, South Merionethshire and West Montgomeryshire. The newspaper's main content included local and district news, together with a list of visitors. From about 1895 it was owned by John Morgan, but was later sold on to David Rowlands (ca. 1910). Richard Hughes Williams (Dic Tryfan, 1878?-1919) was a notable editor from 1913 to 1915."
