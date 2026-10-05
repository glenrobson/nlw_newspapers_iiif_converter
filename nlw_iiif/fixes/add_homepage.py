"""Add a homepage link back to the NLW Welsh Newspapers site.

Manifests are written as <title pid>/<issue pid>.json and link to /view/<issue pid>.
Collections are written as <title pid>/title.json and link to /browse/<title pid>.
"""
from pathlib import Path

NLW_BASE = "https://newspapers.library.wales"


def homepage(url: str, label: str) -> list:
    return [{
        "id": url,
        "type": "Text",
        "label": {"en": [label]},
        "format": "text/html",
        "language": ["en"],
    }]


def fix(data: dict, path: Path) -> bool:
    """Set the homepage on a manifest or title collection. Returns True if data changed."""
    if data.get("type") == "Manifest":
        new = homepage(f"{NLW_BASE}/view/{path.stem}", "NLW webpage for this issue")
    elif data.get("type") == "Collection" and path.name == "title.json":
        new = homepage(f"{NLW_BASE}/browse/{path.parent.name}", "NLW webpage for this title")
    else:
        return False

    if data.get("homepage") == new:
        return False
    data["homepage"] = new
    return True
