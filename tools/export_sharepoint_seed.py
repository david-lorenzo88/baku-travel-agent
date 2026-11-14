#!/usr/bin/env python3
"""Export the shared catalog as SharePoint seed CSVs for the Baku Travel app.

Usage: python tools/export_sharepoint_seed.py
Writes managed-app/sharepoint-seed/Hotels.csv and Activities.csv from
skills-src/_shared/catalog.json (the single source of truth). Column names follow the lists
the Copilot Studio app generator created at the Baku AI Summit (Hotels / Activities), plus
PhotoUrl and PhotoCredit for the Wikimedia photos.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / "skills-src/_shared/catalog.json").read_text(encoding="utf-8"))
out = ROOT / "managed-app/sharepoint-seed"
out.mkdir(parents=True, exist_ok=True)

# Category and Location for activities (not part of the agent's catalog)
ACTIVITY_META = {
    "act-old-city-walking-tour": ("Culture", "Icherisheher"),
    "act-gobustan-mud-volcanoes": ("Day trip", "Gobustan"),
    "act-ateshgah-yanar-dag": ("Day trip", "Absheron Peninsula"),
    "act-boulevard-boat-ride": ("Leisure", "Baku Boulevard"),
    "act-heydar-aliyev-center": ("Architecture", "Narimanov"),
    "act-cooking-class": ("Food", "City centre"),
}

with open(out / "Hotels.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Title", "District", "PricePerPersonNight", "Description", "PhotoUrl", "PhotoCredit"])
    for h in catalog["hotels"]:
        p = h["photos"][0]
        w.writerow([h["name"], h["neighborhood"], h["price_per_person_per_night"], h["description"], p["url"], p["credit"]])

with open(out / "Activities.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Title", "Category", "Description", "Price", "Duration", "Location", "PhotoUrl", "PhotoCredit"])
    for a in catalog["activities"]:
        p = a["photos"][0]
        category, location = ACTIVITY_META[a["id"]]
        w.writerow([a["name"], category, a["description"], a["price_per_person"], a["duration"], location, p["url"], p["credit"]])

print(f"wrote {out / 'Hotels.csv'} and {out / 'Activities.csv'}")
