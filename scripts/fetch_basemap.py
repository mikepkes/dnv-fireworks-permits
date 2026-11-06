#!/usr/bin/env python3
"""Download streets, shoreline, rivers and the District boundary from OpenStreetMap
(Overpass API) and write a simplified data/basemap.json.

Usage: python3 scripts/fetch_basemap.py [--from-file osm.json]
Only needed when you want to refresh the basemap; the result is committed.
"""
import json, math, sys, urllib.request, urllib.parse, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BBOX = "49.285,-123.215,49.42,-122.88"
QUERY = f"""[out:json][timeout:120];
(
 way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|motorway_link|trunk_link|primary_link|secondary_link|living_street)$"]({BBOX});
 way["natural"="coastline"](49.25,-123.3,49.45,-122.8);
 relation["boundary"="administrative"]["name"="District of North Vancouver"];
 way["waterway"="river"]({BBOX});
);
out geom;"""

MAJOR = {"motorway", "trunk", "primary", "motorway_link", "trunk_link", "primary_link"}
MID = {"secondary", "tertiary", "secondary_link"}


def simplify(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy) or 1e-12
    idx, dmax = 0, 0.0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        d = abs(dy * (p[0] - a[0]) - dx * (p[1] - a[1])) / length
        if d > dmax:
            idx, dmax = i, d
    if dmax > eps:
        return simplify(pts[: idx + 1], eps)[:-1] + simplify(pts[idx:], eps)
    return [a, b]


def enc(geom, eps=0.00003):
    pts = simplify([(g["lon"], g["lat"]) for g in geom], eps)
    return [[round(x, 5), round(y, 5)] for x, y in pts]


def main():
    if "--from-file" in sys.argv:
        osm = json.load(open(sys.argv[sys.argv.index("--from-file") + 1]))
    else:
        req = urllib.request.Request(
            "https://overpass-api.de/api/interpreter",
            data=urllib.parse.urlencode({"data": QUERY}).encode(),
            headers={"User-Agent": "dnv-fireworks-permit-map"},
        )
        osm = json.load(urllib.request.urlopen(req, timeout=300))

    out = {k: [] for k in ("major", "mid", "minor", "coast", "river", "bound")}
    names = collections.defaultdict(list)
    for e in osm["elements"]:
        t = e.get("tags", {})
        if e["type"] == "way":
            g = e["geometry"]
            if "highway" in t:
                k = "major" if t["highway"] in MAJOR else "mid" if t["highway"] in MID else "minor"
                line = enc(g)
                out[k].append(line)
                if k != "minor" and t.get("name"):
                    names[t["name"]].append(line)
            elif t.get("natural") == "coastline":
                out["coast"].append(enc(g, 0.00005))
            elif t.get("waterway") == "river":
                out["river"].append(enc(g, 0.00005))
        elif e["type"] == "relation":
            for m in e["members"]:
                if m.get("role") == "outer" and "geometry" in m:
                    out["bound"].append(enc(m["geometry"], 0.00006))

    labels = []
    for n, ls in names.items():
        best = max(ls, key=len)
        if len(best) < 4:
            continue
        p = best[len(best) // 2]
        q = best[min(len(best) // 2 + 1, len(best) - 1)]
        ang = math.degrees(math.atan2(-(q[1] - p[1]), (q[0] - p[0]) * math.cos(math.radians(49.33))))
        ang = ang - 180 if ang > 90 else ang + 180 if ang < -90 else ang
        labels.append((sum(len(l) for l in ls), n, p, round(ang)))
    labels.sort(reverse=True)
    out["labels"] = [[n, p[1], p[0], a] for _, n, p, a in labels[:28]]

    path = ROOT / "data" / "basemap.json"
    path.write_text(json.dumps(out, separators=(",", ":")))
    print(f"wrote {path} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
