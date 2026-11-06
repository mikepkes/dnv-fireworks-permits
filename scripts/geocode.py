#!/usr/bin/env python3
"""Geocode any discharge address in data/permits.csv that is not yet in data/geocodes.csv,
using the BC Address Geocoder (https://geocoder.api.gov.bc.ca). Existing rows are never
changed, so hand corrections in geocodes.csv are kept.

Usage: python3 scripts/geocode.py
"""
import csv, json, pathlib, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
PERMITS = ROOT / "data" / "permits.csv"
GEOCODES = ROOT / "data" / "geocodes.csv"
FIELDS = ["address", "lat", "lon", "match_precision", "score", "matched_address", "source"]


def key(addr):
    return " ".join(addr.split()).upper()


def lookup(addr):
    q = urllib.parse.urlencode({
        "addressString": f"{addr}, District of North Vancouver, BC",
        "maxResults": 1,
        "locationDescriptor": "parcelPoint",
    })
    req = urllib.request.Request(
        "https://geocoder.api.gov.bc.ca/addresses.json?" + q,
        headers={"User-Agent": "dnv-fireworks-permit-map"},
    )
    f = json.load(urllib.request.urlopen(req, timeout=30))["features"][0]
    p = f["properties"]
    lon, lat = f["geometry"]["coordinates"]
    return {"address": addr, "lat": lat, "lon": lon, "match_precision": p["matchPrecision"],
            "score": p["score"], "matched_address": p["fullAddress"], "source": "BC Address Geocoder"}


def main():
    rows = list(csv.DictReader(GEOCODES.open())) if GEOCODES.exists() else []
    known = {r["address"] for r in rows}
    wanted = sorted({key(r["discharge_address"]) for r in csv.DictReader(PERMITS.open())})
    new = [a for a in wanted if a not in known]
    for a in new:
        r = lookup(a)
        rows.append(r)
        flag = "" if int(r["score"]) >= 90 and r["match_precision"] in ("CIVIC_NUMBER", "UNIT") else "  <-- check"
        print(f"{a} -> {r['matched_address']} ({r['match_precision']}, score {r['score']}){flag}")
    rows.sort(key=lambda r: r["address"])
    with GEOCODES.open("w", newline="") as fh:
        w = csv.DictWriter(fh, FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(new)} new address(es) geocoded; {len(rows)} total")


if __name__ == "__main__":
    main()
