#!/usr/bin/env python3
"""Downloads an openly licensed image into daily/img/ and prints its <figure> credit line.

Two modes, run from the repo root:

  Wikimedia Commons (license and author read from the Commons API):
    fetch_image.py commons "File:Example.jpg" --out daily/img/2026-11-10-example.jpg

  A public-domain U.S. government image (you confirm the license on its page first):
    fetch_image.py url https://www.cdc.gov/.../photo.jpg --out daily/img/x.jpg \
        --page https://www.cdc.gov/... --author "CDC" --license "Public domain (U.S. government work)"

Refuses Commons files whose license isn't public domain, CC0, CC BY or CC BY-SA.
Resizes to at most 1200px wide and strips metadata. Prints the HTML for the
figcaption credit, which build_site.py requires.
"""

import argparse
import html
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

UA = "daily-parenting-page/1.0 (https://github.com/frizfealer/pregancy_knowledge_base)"
OK_LICENSE = re.compile(r"^(public domain|pd|cc0|cc[ -]by(-sa)?[ -]?\d)", re.I)


def get(url, tries=4):
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i < tries - 1:
                time.sleep(3 * (i + 1))
                continue
            raise


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def commons(title):
    """Returns (file url, page url, author, license name, license url)."""
    q = urllib.parse.urlencode({"action": "query", "titles": title, "prop": "imageinfo",
                                "iiprop": "url|extmetadata", "format": "json"})
    data = json.loads(get(f"https://commons.wikimedia.org/w/api.php?{q}"))
    page = next(iter(data["query"]["pages"].values()))
    if "imageinfo" not in page:
        sys.exit(f"{title}: not found on Commons")
    info = page["imageinfo"][0]
    meta = info["extmetadata"]
    lic = strip_tags(meta.get("LicenseShortName", {}).get("value"))
    if not OK_LICENSE.match(lic):
        sys.exit(f"{title}: license {lic!r} isn't public domain, CC0, CC BY or CC BY-SA; don't use it")
    author = strip_tags(meta.get("Artist", {}).get("value")) or "unknown author"
    if len(author) > 120 or re.search(r"not in the public domain|please|send me|permission", author, re.I):
        sys.exit(f"{title}: the author field adds conditions beyond the license; pick another image:\n{author[:400]}")
    lic_url = meta.get("LicenseUrl", {}).get("value", "")
    return info["url"], info["descriptionurl"], author, lic, lic_url


def save(raw, out):
    img = Image.open(io.BytesIO(raw))
    img = img.convert("RGB") if img.mode not in ("RGB", "L") and out.suffix.lower() in (".jpg", ".jpeg") else img
    if img.width > 1200:
        img = img.resize((1200, round(img.height * 1200 / img.width)), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    params = {"quality": 85, "optimize": True} if out.suffix.lower() in (".jpg", ".jpeg") else {"optimize": True}
    img.save(out, **params)  # re-encoding drops EXIF and other metadata
    return img.width, img.height


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["commons", "url"])
    ap.add_argument("source", help='"File:Name.jpg" for commons, or the image URL')
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--page", help="url mode: the page that shows the image and its license")
    ap.add_argument("--author")
    ap.add_argument("--license")
    a = ap.parse_args()

    if a.mode == "commons":
        url, page, author, lic, lic_url = commons(a.source)
    else:
        if not (a.page and a.author and a.license):
            sys.exit("url mode needs --page, --author and --license")
        url, page, author, lic, lic_url = a.source, a.page, a.author, a.license, ""
    w, h = save(get(url), a.out)
    lic_html = f'<a href="{html.escape(lic_url)}">{html.escape(lic)}</a>' if lic_url else html.escape(lic)
    print(f"saved {a.out} ({w}x{h})")
    print(f'<span class="credit">{html.escape(author)} · {lic_html} · <a href="{html.escape(page)}">source</a></span>')


if __name__ == "__main__":
    main()
