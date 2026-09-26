import re
from datetime import date, datetime

from bs4 import BeautifulSoup
from iiif_prezi3 import Collection, config, KeyValueString, ManifestRef

config.configs["helpers.auto_fields.AutoLang"].auto_lang = "en"


def parse_title_page(soup: BeautifulSoup) -> dict:
    """Extract newspaper title metadata and links to its issues.

    TODO: update selectors once we've looked at the real title page markup.
    """
    heading = soup.select_one("h1.card-title.accessible-card-title")
    summary = soup.select_one("h1.card-title.accessible-card-title ~ p.card-text")
    details = parse_pub_details(soup)
    return {
        "label": heading.get_text(strip=True) if heading else "Untitled newspaper",
        "summary": summary.get_text(strip=True) if summary else None,
        "copyright": details.get("copyright"),
        "frequency": details.get("frequency"),
        "publisher": details.get("publisher"),
        "dates": details.get("issue dates"),
        "issues": parse_issues(soup),
    }


def parse_pub_details(soup: BeautifulSoup) -> dict:
    """Read the "LABEL: value" publication details, e.g. {"frequency": "Weekly"}."""
    details = {}
    for div in soup.select("div.pub-details"):
        label_tag = div.find("strong")
        if not label_tag:
            continue
        label = label_tag.get_text(strip=True).rstrip(":").strip().lower()
        # The value is the div's own text, excluding the label and any
        # extra notes such as "<p>(2,570 available issues)</p>".
        value = " ".join(
            text.strip() for text in div.find_all(string=True, recursive=False) if text.strip()
        )
        details[label] = value
    return details

def parse_issues(soup: BeautifulSoup) -> list:
    """Read the issues getting the date and the PID for each issue"""
    issues = []
    for link in soup.select("ul.issue-list li a[href^='/view/']"):
        pid = link["href"].removeprefix("/view/").strip("/")
        number = link.find("strong")
        if number:
            number.extract()  # drop the "1." list number, leaving e.g. "Saturday 19th June 1858"
        name = " ".join(link.get_text().split())  # collapse newlines/indentation to single spaces
        issues.append({"pid": pid,
                       "name": name,
                       "date": parse_issue_date(name)})
    return issues


def parse_issue_date(text: str) -> date:
    """Parse e.g. "Saturday 19th June 1858" into a date."""
    text = " ".join(text.split())
    text = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", text)
    return datetime.strptime(text, "%A %d %B %Y").date()


def build_collection(collection_id: str, title: dict) -> Collection:
    """Create a IIIF Collection for a newspaper title."""
    collection = Collection(id=collection_id, label=title["label"], summary=title["summary"])

    collection.metadata = [
        KeyValueString(label="Frequency", value=title["frequency"]),
        KeyValueString(label="Publisher", value=title["publisher"]),
        KeyValueString(label="Issue dates", value=title["dates"]),
    ]

    if title["copyright"] == "UNKNOWN":
        collection.rights = "https://rightsstatements.org/vocab/UND/1.0/"
    else:
        print (f'Unmatched copyright status {title["copyright"]}')    
        exit(-1)

    # Issue manifests are added as references once they have been generated, e.g.
    # collection.add_item(manifest) or collection.make_manifest(id=..., label=...)
    return collection

def add_issues(title: Collection, issues: list, base_id: str):
    for issue in issues:
        title.add_item(ManifestRef(
                id=f"{base_id}/{issue["pid"]}.json",
                type="Manifest",
                label=issue["name"],
                navDate=issue["date"]
                ))