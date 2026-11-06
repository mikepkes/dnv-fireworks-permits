# Contributing

Thanks for helping keep the map accurate. All changes go through pull requests.

## Ground rules

- **Cite a public source** for every new fact (a seller's address, a corrected location, a new release). Put the link in the CSV row or the PR description.
- **Don't add personal information** beyond what the District released. No names, phone numbers or photos of homes.
- **Keep `data/permits.csv` faithful to the release.** If you think a released value is wrong, say so in the PR and fix the *location* in `geocodes.csv` instead of editing the permit row.

## Fixing a location

1. Find the address in `data/geocodes.csv` (addresses are upper case, as released).
2. Update `lat` and `lon` (WGS84, decimal degrees).
3. Set `source` to how you checked it, for example `manual: DNV GeoWeb parcel`.

## Adding a seller

Add a row to `data/sellers.csv`:

| column | example |
|---|---|
| `address` | `1089 MARINE DR` |
| `seller` | `Phatboy Fireworks` |
| `years_confirmed` | `2025;2026` (semicolon-separated, blank if unknown) |
| `source` | short description of the source |
| `source_url` | link |

If the address isn't already in `geocodes.csv`, add it there too (or run `python3 scripts/geocode.py` after adding a permit row that uses it).

## Adding permit data

Put the original file under `data/source/`, append rows to `data/permits.csv` with `source_row` and `foi_request` filled in, then run:

```sh
python3 scripts/geocode.py
python3 scripts/build.py
```

The page's year filter currently handles 2025 and 2026; the build will tell you if a new year needs a page change.
