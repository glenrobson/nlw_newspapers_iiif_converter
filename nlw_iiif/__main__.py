import argparse
import json
from pathlib import Path

from .fetch import get_soup
from .title import build_collection, parse_title_page, parse_issues, add_issues
from .issue import parse_issue_page, build_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a IIIF Collection from an NLW newspaper title page.")
    parser.add_argument("pid", help="PID for the newspaper title page")
    parser.add_argument("--base-id", default="https://glenrobson.github.io/nlw_newspapers_iiif_converter/newspapers", help="Base URI for generated IIIF ids")
    parser.add_argument("--output", type=Path, default=Path("newspapers"), help="Directory to write JSON to")
    args = parser.parse_args()

    soup = get_soup(f"https://newspapers.library.wales/browse/{args.pid}")
    title = parse_title_page(soup)
    collection = build_collection(f"{args.base_id}/{args.pid}/title.json", title)

    soup = get_soup(f"https://newspapers.library.wales/browse/{args.pid}/list")
    issues = parse_issues(soup)
    add_issues(collection, issues, f"{args.base_id}/{args.pid}")

    out_file = args.output / args.pid / "title.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(json.loads(collection.jsonld()), indent=2))

    for issue in issues:
        soup = get_soup(f"https://newspapers.library.wales/view/{issue["pid"]}")
        issue_data = parse_issue_page(soup)

        manifest = build_manifest(f"{args.base_id}/{args.pid}/{issue["pid"]}.json", title, issue_data)

        out_file = args.output / args.pid / f"{issue["pid"]}.json"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(json.loads(manifest.jsonld()), indent=2))

        break

    print(f"Found title: {title['label']}")
    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
