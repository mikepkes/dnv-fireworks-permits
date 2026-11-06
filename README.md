# District of North Vancouver fireworks permits, 2025–2026

An interactive map of every fireworks discharge permit the District of North Vancouver (DNV) issued for Halloween 2025 and 2026, from the District's response to freedom-of-information request **26-214**.

**[Open the map →](https://mikepkes.github.io/dnv-fireworks-permits/)**

- 579 permits (285 in 2025, 294 in 2026) at 412 discharge addresses
- Filter by year; dot size shows how many permits named the same address

## What's in the data

| File | What it is |
|---|---|
| `data/source/FOI-26-214-fireworks-permits-2025-2026.xlsm` | The spreadsheet exactly as released by the District |
| `data/permits.csv` | One row per permit, transcribed from the release. `source_row` is the row in the original spreadsheet. Whitespace is tidied; nothing else is changed. |
| `data/geocodes.csv` | Coordinates for each discharge address, from the [BC Address Geocoder](https://www2.gov.bc.ca/gov/content/data/geographic-data-services/location-services/geocoder). `match_precision` other than `CIVIC_NUMBER`/`UNIT` means the point is approximate. |
| `data/sellers.csv` | Research notes on fireworks retailer locations. Only rows marked `verified` = `yes` are shown on the map; none are yet. |
| `data/basemap.json` | Simplified streets, shoreline and District boundary from OpenStreetMap |

### Things to know before drawing conclusions

- **Applicants don't have to live in the District.** The permit requires discharge on private property in the District, with the owner's permission. `applicant_municipality` is free text typed by the applicant.
- **The discharge address is self-reported** and the District has said entries are not corrected before a permit is issued.
- **Some addresses carry many permits.** 1089 Marine Dr, a commercial address, is the discharge address on 18 permits (17 in 2025).
- **Row order** in the release is not documented. It may reflect issue order, but that is not confirmed.
- The release has no names, dates, quantities or how each permit was issued.

## Contributing

Corrections and additions are welcome by pull request. See [CONTRIBUTING.md](CONTRIBUTING.md). Common ones:

- **A dot is in the wrong place:** fix the row in `data/geocodes.csv` and set `source` to say how you checked it.
- **Retailer locations:** add a row to `data/sellers.csv` with a source. Set `verified` to `yes` only with a reliable source, such as a District business licence record or vendor list for that season.
- **New FOI data** (another year, or more fields): add the release under `data/source/` and the rows to `data/permits.csv`.

Every pull request is built automatically; the build fails if any permit can't be placed on the map. Merges to `main` publish the map to GitHub Pages.

## Building locally

Python 3, standard library only.

```sh
python3 scripts/geocode.py      # only needed if permits.csv has new addresses
python3 scripts/build.py        # writes site/index.html
open site/index.html
```

`scripts/fetch_basemap.py` refreshes the OpenStreetMap basemap; you rarely need it.

## Sources and licences

- Permit data: District of North Vancouver, FOI request 26-214 release package.
- Geocoding: BC Address Geocoder, © Province of British Columbia, [Open Government Licence – British Columbia](https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc).
- Basemap (`data/basemap.json`): © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under the [Open Database License](https://opendatacommons.org/licenses/odbl/).
- Map library: [Leaflet](https://leafletjs.com) 1.9.4 (BSD-2-Clause).
- Code in `scripts/` and `src/template.html`: MIT, see [LICENSE](LICENSE).

This map shows addresses as the District released them. A permit at an address says nothing about who lives there.
