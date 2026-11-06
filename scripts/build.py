#!/usr/bin/env python3
"""Build site/index.html from the CSV data, the basemap and src/template.html.
Standard library only. Fails loudly if any permit cannot be placed on the map.

Usage: python3 scripts/build.py
"""
import collections, csv, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data"
OUT = ROOT / "site" / "index.html"
STACK_OFFSET = 0.00012  # ~9 m east, so addresses that geocode to the same point stay visible


def key(addr):
    return " ".join(addr.split()).upper()






def main():
    permits = list(csv.DictReader((D / "permits.csv").open()))
    geo = {r["address"]: r for r in csv.DictReader((D / "geocodes.csv").open())}
    sellers = list(csv.DictReader((D / "sellers.csv").open()))

    counts = collections.defaultdict(lambda: collections.Counter())
    years = set()
    for p in permits:
        counts[key(p["discharge_address"])][p["year"]] += 1
        years.add(p["year"])
    missing = sorted(a for a in counts if a not in geo)
    if missing:
        sys.exit("No coordinates for: " + ", ".join(missing) + "\nRun scripts/geocode.py first.")
    if years - {"2025", "2026"}:
        sys.exit(f"Unexpected years {sorted(years)}: the page filter currently supports 2025 and 2026.")

    pts, seen = [], collections.Counter()
    for a in sorted(counts):
        g = geo[a]
        lat, lon = float(g["lat"]), float(g["lon"])
        spot = (round(lat, 5), round(lon, 5))
        lon += STACK_OFFSET * seen[spot]
        seen[spot] += 1
        approx = g["match_precision"] not in ("CIVIC_NUMBER", "UNIT")
        pts.append([a.title(), round(lat, 6), round(lon, 6), counts[a]["2025"], counts[a]["2026"], approx])

    total = sum(c["2025"] + c["2026"] for c in counts.values())
    assert total == len(permits), "permit count mismatch"

    by_addr = collections.defaultdict(list)
    for s in sellers:
        # Only verified sellers are published on the map; unverified rows are research notes.
        if s.get("verified", "").strip().lower() in ("yes", "true", "1"):
            by_addr[key(s["address"])].append(s)
    seller_out = []
    for a, ss in by_addr.items():
        if a not in geo:
            sys.exit(f"Seller address {a} has no coordinates; add it to data/geocodes.csv.")
        seller_out.append({
            "addr": a.title(),
            "lat": float(geo[a]["lat"]), "lon": float(geo[a]["lon"]),
            "names": [s["seller"] for s in ss],
            "years": sorted({y.strip() for s in ss for y in s["years_confirmed"].split(";") if y.strip()}),
            "sources": [{"label": s["source"], "url": s["source_url"]} for s in ss],
            "c25": counts[a]["2025"], "c26": counts[a]["2026"],
        })

    data = json.loads((D / "basemap.json").read_text())
    data["pts"] = pts
    data["sellers"] = seller_out
    html = (ROOT / "src" / "template.html").read_text()
    html = html.replace("/*LEAFLET_CSS*/", (ROOT / "src" / "leaflet-1.9.4.min.css").read_text())
    html = html.replace("/*DATA_JS*/", "window.DATA=" + json.dumps(data, separators=(",", ":")) + ";")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(f"Built {OUT.relative_to(ROOT)}: {len(permits)} permits, {len(pts)} addresses, {len(seller_out)} seller locations")


if __name__ == "__main__":
    main()
