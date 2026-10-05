"""Apply a fix to already generated IIIF manifests and collections.

Each fix is a module in this package with a function:

    def fix(data: dict, path: Path) -> bool

which edits the parsed JSON in place and returns True if it changed anything.
Only changed files are rewritten.

Usage: python -m nlw_iiif.fixes.run_fix add_homepage newspapers/
"""
import argparse
import importlib
import json
from pathlib import Path


def run_fix(fix_name: str, directory: Path) -> None:
    fix = importlib.import_module(f"{__package__}.{fix_name}").fix

    changed = 0
    total = 0
    for path in sorted(directory.rglob("*.json")):
        total += 1
        data = json.loads(path.read_text())
        if fix(data, path):
            path.write_text(json.dumps(data, indent=2))
            changed += 1

    print(f"{fix_name}: updated {changed} of {total} files in {directory}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a fix to generated IIIF JSON files.")
    parser.add_argument("fix", help="Name of the fix module in nlw_iiif/fixes, e.g. add_homepage")
    parser.add_argument("directory", type=Path, help="Directory of manifests/collections (searched recursively)")
    args = parser.parse_args()

    run_fix(args.fix, args.directory)


if __name__ == "__main__":
    main()
