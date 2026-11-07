# Bay State Eats (ma-eats) — notes for Claude Code sessions

Built 2026-11-06 by a side session for Nick's "build the 17 remaining states" (group: Massachusetts, New Hampshire, New Mexico, Montana),
ported from `../va-eats/` with every fix to 2026-11-05 (delivery-only brands hidden, the shared website blocklist and
`link_blocklist.py`, the Share link to `Links.site + explore/#p=<id>`, OTA data, the widened adult rule with Vermont's and Virginia's
fixes, the Denny's delivery-brand guard, Utah's street-word merge fix, the exact-outline county lookup). Local only: git-ignored data,
no repo, no remote, nothing published. Sources and calibration: `playbook/12-sources.md`. Brand: `playbook/05-naming.md` —
**final** (Nick's decisions, 2026-11-07: "Bay State Eats: Massachusetts", Home Screen "Bay State Eats"; a chowder bowl icon, concept
B, on Atlantic navy; navy #13294B, cranberry #9E1B32, Cape sand #E2B25A fill only, chowder cream #F7F2E6; a band of Atlantic swells
with the Cape's hook).

## Massachusetts is different
- **No Google data at all**, in either build (Nick's rule for these four states): `listings.py` reads no UCSD snapshot; calibration is
  against the official city lists.
- **Towns:** the 351 cities and towns from Overture's locality outlines (`fetch_overture.py` writes `ma_towns_detail.geojson`: 363
  localities less 13 villages, plus Nantucket). Each listing's town is the outline its point is in; its postal name stays as `area`
  (`ar` in the app data: "Dorchester, Boston", "Hyannis, Barnstable"), searchable. `canon_city` maps neighborhoods and villages for
  research and records (`BOSTON_HOODS`, `VILLAGE_TOWN`, and `data/ma/locality_town.json`, which `listings.py` derives). Counties (14)
  only split the detail files into 7 regions.
- **Official data:** Cambridge's food permits and sanitary inspections (PDDL) and Somerville's food permits and licenses (ODbL), from
  their Socrata portals (`fetch_official.py`, `official.py`). Cambridge's inspections show as the city words them ("No violations cited"
  or "Violations cited" plus the Food Code sections), dated, never a grade. Somerville's "Restaurant (with alcohol)" license is the only
  "Serves alcohol" signal. **Boston's data portal answers scripts with a Cloudflare Turnstile 403** (and robots.txt disallows /api/ and
  /datastore/): not read, never bypassed; Boston places link to the Mayor's Food Court search. Nick's call whether to ask the City.
- **Honors:** MICHELIN Guide Boston (November 2025; Greater Boston only): 311 Omakase ★, six Bib Gourmands, 19 recommended. James Beard:
  Sullivan's Castle Island (America's Classics 2025), 2025 finalists Sarma, Urban Hearth and Merai, 2025-26 semifinalists. No
  Massachusetts finalist or winner in 2026. The facts for all four states are in the shared notes, `jbf-ma-nh-nm-mt-2025-26.md`.
- **Guides** (tags in `massachusetts.py` TAGS, bits 1..128): North Shore roast beef, clam shacks & lobster rolls, North End Italian,
  Portuguese, classic diners, Chinatown dim sum & bakeries, historic taverns & inns, oldest. Sources in `pipeline/build_research.py`
  (Tasting Table, Chowhound, Meet Boston, Cape Cod Chamber, Discover Central MA, North of Boston, WBSM). visitma.com (state tourism) is
  behind a Cloudflare challenge: not used. Leads (bar pizza, older JBF honors, Taiwan Bakery's name) in `data/research/app/LEADS.md`.
- **Venues:** Logan's terminals (by box and address), Worcester's airport, the stadiums and arenas, the bases, the prisons.
- **Inspections:** only on place pages (no inspection list among the guides), per Nick's 11-05 call.
- **Ranking:** "Featured first" (honors, then founding year), as everywhere; no health-grade wording.

## Rebuild
```bash
cd pipeline
../.venv/bin/python check_sources.py URL...   # a new host first
../.venv/bin/python fetch_overture.py && ../.venv/bin/python fetch_extras.py && ../.venv/bin/python fetch_official.py
../.venv/bin/python geocode_official.py && ../.venv/bin/python listings.py && ../.venv/bin/python calibrate.py
../.venv/bin/python massachusetts.py && ../.venv/bin/python build_research.py && ../.venv/bin/python massachusetts.py
../.venv/bin/python geocode_census.py   # research addresses the map lacks (data/research/geocode_todo.json), then massachusetts.py again
MA_APP=1 ../.venv/bin/python massachusetts.py && cd .. && cp data/app/places.json data/app/detail-*.json MassachusettsEats/Resources/
cd pipeline && ../.venv/bin/python check_websites.py && ../.venv/bin/python check_websites.py --retry-transient && cd ..   # then re-export
.venv/bin/python scripts/make-site.py && .venv/bin/python scripts/publish_app_data.py && .venv/bin/python scripts/publish_app_data.py --check
.venv/bin/python scripts/qa-site.py --static
```
(`listings.py` before `calibrate.py`; `massachusetts.py` once before `build_research.py`, which matches names against
`site/massachusetts.json`.) The `.venv` is a copy of wy-eats' (python.org framework Python 3.12, md-eats' package versions).

## App, site, screenshots
- App: `MassachusettsEats/` (XcodeGen `project.yml`, bundle `com.massachusettseats.ios`, display "Bay State Eats"), tests in
  `MassachusettsEatsTests/` (data guards: adult venues, blocklisted and multi-URL websites, bad and legal names, non-restaurants, listed
  twice, no Google data; the outline with Pawtucket, Salem NH, Nashua, Enfield CT, Pownal VT, Hillsdale NY and Block Island outside) and
  `MassachusettsEatsUITests/`. Run with `DEVELOPER_DIR="/Applications/Xcode 1.app/Contents/Developer"`; unit tests may use
  `CODE_SIGNING_ALLOWED=NO`, UI tests need the signed runner (no flag). Archive only with Xcode 1.app (27.2, 27B52). Run `xcodegen
  generate` whenever the set of `Resources/*.json` files changes.
- Site: `scripts/make-site.py` writes `docs/` and `playbook/site-numbers.json`; `scripts/explore.js` is the web app (it searches the
  `ar` area too); `scripts/qa-site.py` the QA. Site URL for now: nickstrom5.github.io/massachusetts-eats (no CNAME). Rebuild the site
  before the unit tests (`ShareLinkTests` reads `docs/`).
- OTA data: `docs/data/app/` via `scripts/publish_app_data.py` (`../OTA-DATA.md`).
- Screenshots: `scripts/capture-screenshots.sh <sim>` (ScreenshotMode pins Faneuil Hall; Salem for roast beef, Worcester for diners,
  Fall River for Portuguese), then `scripts/site-images.sh`, then make-site + qa-site. App Store frames: `scripts/appstore-screenshots.py`.
  Icons: `scripts/icon-concepts.swift` and `scripts/make-brand.swift` (concept B).

## Status (2026-11-07): ready to publish
- Data: 15,908 places, 15,519 restaurants in 327 towns (QCEW 15,580); 75 hand-checked on a guide, 45 MICHELIN or James Beard honorees,
  368 Cambridge inspection results, 66 Somerville "serves alcohol" licenses. Links checked 2026-11-06 (9,520 of 14,158 ok); a field
  holding two URLs is dropped (the export now refuses whitespace in a website).
- Tests: unit (49) and UI tests pass on iPhone 17 Pro Max and iPad Pro 13" (iOS 27.0, Xcode 1.app). Screenshots in docs/screenshots and
  playbook/app-store/{iphone,ipad} (8 + 6 frames). Site: 19 pages; `qa-site.py` (full, with the web app) passes. OTA 2026-11-06.1
  published locally (`--check` OK). Listing: playbook/app-store/listing.json.
- 18:00 fix: a guide phrase starting with a street word ("north end", "north shore beef": "north" maps to "n") didn't select its guide
  in the app or the web app; both now match the words as typed too (with a unit test). Rerun after the fix: unit (49) and UI tests pass
  and `qa-site.py` (full) passes.
  Launch-time check: passed on iPhone on a quiet Mac, 5.14 s (the QA session, 2026-11-07); the iPad pass was running then.
- Records: the QA session is drafting the request to Boston for its inspection data, for Nick.

## Rules
No commits, pushes, public repos, App Store Connect or DNS changes without Nick's yes each time; never submit for review or accept
agreements; never publish Google-derived data. Support email nick@eatsranked.com. Commit author "Nick Soderstrom"
<329204362+nickstrom5@users.noreply.github.com> via `-c user.name -c user.email`.
