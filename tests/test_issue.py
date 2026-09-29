from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from nlw_iiif import fetch
from nlw_iiif.fetch import get_soup
from nlw_iiif.issue import parse_issue_page

FIXTURES = Path(__file__).parent / "fixtures"
TITLE_URL = "https://newspapers.library.wales/view/3036869"
TITLE_HTML = (FIXTURES / "issue.html").read_text(encoding="utf-8")


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

    issue = parse_issue_page(get_soup(TITLE_URL))

    assert issue["label"] == "19th June 1858"

    assert issue["pages"][0]["pid"] == "03036870"
    assert issue["pages"][1]["pid"] == "03036871"

    assert len(issue["pages"]) == 2
