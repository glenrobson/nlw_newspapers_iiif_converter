from bs4 import BeautifulSoup
from iiif_prezi3 import Manifest,KeyValueString
from datetime import date, datetime
import re

def parse_issue_page(soup: BeautifulSoup) -> dict:
    """Extract issue metadata and its page images.

    TODO: update selectors once we've looked at the real issue page markup.
    """
    heading = soup.select_one("div.issue-date")
    return {
        "label": heading.get_text(strip=True) if heading else "Untitled issue",
        "pages": parse_pages(soup)
    }

def parse_issue_date(text: str) -> date:
    """Parse e.g. 19th June 1858 ."""
    text = " ".join(text.split())
    text = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", text)
    return datetime.strptime(text, "%d %B %Y").date()


def parse_pages(soup: BeautifulSoup) -> list:
    """Read the page dropdown, e.g. [{"label": "Page 1", "pid": "3036870"}, ...]."""
    pages = []
    # The page controls appear twice (above and below the viewer); only read the first.
    menu = soup.select_one("#page-controls ul.dropdown-menu")
    if not menu:
        return pages
    for link in menu.select("li a[href]"):
        pages.append({
            "label": " ".join(link.get_text().split()),
            "pid": "0" + link["href"].rstrip("/").rsplit("/", 1)[-1],
        })
    return pages


def build_manifest(manifest_id: str, title: dict, issue: dict) -> Manifest:
    """Create a IIIF Manifest for a single newspaper issue."""
    manifest = Manifest(id=manifest_id, label=issue["label"])

    manifest.metadata = [
        KeyValueString(label="Title", value=title["label"]),
        KeyValueString(label="Frequency", value=title["frequency"]),
        KeyValueString(label="Publisher", value=title["publisher"]),
        KeyValueString(label="Issue dates", value=title["dates"]),
    ]

    if title["copyright"] == "UNKNOWN":
        manifest.rights = "https://rightsstatements.org/vocab/UND/1.0/"
    else:
        print (f'Unmatched copyright status {title["copyright"]}')    
        exit(-1)

    base_url = manifest_id.replace(".json","")

    for i, page in enumerate(issue["pages"], start=1):

        manifest.make_canvas_from_iiif(url=f"https://iiif.llyfrgell.cymru/iiif/{page.get("pid")[0:2]}/{page.get("pid")[2:5]}/{page.get("pid")}.jp2",
                                        id=f"{base_url}/canvas/{i}",
                                        label=page.get("label", f"Page {i}"),
                                        anno_id=f"{base_url}/annotation/{i}",
                                        anno_page_id=f"{base_url}/page/{i}")
       
    return manifest
