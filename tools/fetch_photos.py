#!/usr/bin/env python3
"""Download, check and resize the catalog photos for the PDF skill (dev only).

Usage: python tools/fetch_photos.py [--catalog PATH] [--out DIR]

For every photo in the shared catalog: checks the URL returns HTTP 200 with an image content
type, downloads it, resizes it to max 800 px wide JPEG ≤ 200 KB and saves it under the PDF
skill's assets/photos/ folder. Exits 1 and lists every failed URL if any photo fails.
Sends a generic User-Agent (no personal details), as Wikimedia requires for automated clients.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
UA = "baku-travel-agent-dev/1.0"
MAX_WIDTH = 800
MAX_BYTES = 200 * 1024


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                ctype = r.headers.get("Content-Type", "")
                if r.status != 200 or not ctype.startswith("image/"):
                    raise ValueError(f"HTTP {r.status}, content type {ctype!r}")
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                time.sleep(5 * (attempt + 1))
                continue
            raise
    raise RuntimeError("unreachable")


def resize(data: bytes) -> bytes:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    if img.width > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, round(img.height * MAX_WIDTH / img.width)), Image.LANCZOS)
    for quality in (85, 75, 65, 55, 45):
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=quality, optimize=True)
        if buf.tell() <= MAX_BYTES:
            return buf.getvalue()
    raise ValueError("could not compress below 200 KB")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default=str(ROOT / "skills-src/_shared/catalog.json"))
    ap.add_argument("--out", default=str(ROOT / "skills-src/export-trip-plan-pdf/assets/photos"))
    args = ap.parse_args()

    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    failures = []
    for item in catalog["hotels"] + catalog["activities"]:
        for photo in item["photos"]:
            try:
                data = resize(download(photo["url"]))
                (out / photo["file"]).write_bytes(data)
                print(f"ok   {photo['file']:40} {len(data) // 1024:4d} KB")
                time.sleep(1)
            except Exception as exc:  # report every failure, keep going
                failures.append(f"{item['id']}: {photo['url']} ({exc})")
                print(f"FAIL {photo['file']}: {exc}")
    if failures:
        print(f"\n{len(failures)} photo(s) failed:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nall photos ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
