# Massachusetts sources and calibration (checked 2026-11-06)

## Official sources
| Source | What it has | Can a script read it? | Used |
|---|---|---|---|
| Cambridge ISD "Sanitary Inspections" (data.cambridgema.gov `ryb9-qzmw`, Open Data Commons PDDL, rows updated 2026-11-02) | 12,078 rows: one per citation (Food Code section, description, date corrected), and one with no code for an inspection that found none; 3,667 cases, case dates 2021-05 to 2026-10-14 (828 rows and some 2022-23 cases carry no inspection date) | yes (Socrata API; robots.txt allows /resource/, Crawl-delay 1) | yes: 3,123 dated inspections, 2,789 joined to a permit; the latest per place, "No violations cited" or "Violations cited" plus the codes, dated, never a grade |
| Cambridge "Food Establishment Permits" (`iect-ma2e`, PDDL, updated daily) | 7,061 yearly permits (2018-2026), dba, address, point, permit kind (Non Alcohol, Alcohol, Bakery, Retail, Package, Wholesale, Daycare, Institution) | yes | yes: 1,578 businesses, 924 current (issued since 2025-07-01); the dba only, never `applicant_name` or the legal `business_name` |
| Somerville "Applications for Permits and Licenses" (data.somervillema.gov `nneb-s3f7`, ODbL, SomerStat, updated daily) | active Food Establishment (Food Service 310, Retail Food, School, Caterer, Mobile), Common Victualer (155) and "Restaurant (with alcohol)" (126) records | yes | yes: 764 active records; the Restaurant (with alcohol) license is the app's only "Serves alcohol" signal (66 restaurants); no applicant or contractor fields read |
| Boston ISD "Food Establishment Inspections" (data.boston.gov, resource `4582bec6-…`, PDDL) and the licensing datasets | daily inspections since 2006; active food and Licensing Board licenses | **no**: every data.boston.gov page answers scripts with a Cloudflare Turnstile 403 ("Turnstile verification required", 2026-11-06), and robots.txt disallows /api/ and /datastore/ | not read, never bypassed; Boston places link to the city's own search, boston.gov/departments/inspectional-services/mayors-food-court (200). **Nick's call**: ask the City for access or a bulk copy |
| Worcester "Food Establishment Licenses" (ArcGIS) | addresses, no business names | yes | no (no names to match) |
| DPH / mass.gov | no statewide inspection data; each city's or town's board of health inspects under 105 CMR 590.000 | mass.gov answered 403 to scripts in September 2026 | no |

No other city publishes food permits or inspections as open data (the prompt's list: Springfield, Lowell, Brockton, New Bedford, Quincy,
Lynn, Fall River, Newton, Brookline, Salem: search pages at most, not read). No statewide liquor licensee list (each town's licensing
board issues Section 12 licenses; the ABCC was not checked further).

## Towns
The place filter is the 351 cities and towns: Overture's locality outlines for Massachusetts (363) less the 13 villages it also lists
(Hyannis, Osterville, Centerville, Cotuit, Marstons Mills, West Barnstable, Village of Barnstable, Dennisport, South Dennis, West Dennis,
Village of Nagog Woods, Pontoosuc, Rings Island), plus Nantucket (town = county). Each map listing takes the town its point is in
(listings.py); the postal name stays as the place's `area` ("Dorchester, Boston", "Hyannis, Barnstable"), searchable. 475 listings'
points sat in another town than their postal name. Counties (14) only split the app's detail files into 7 regions.

## Calibration (official lists vs. map listings, by city)
- BLS QCEW: 15,580 private NAICS 722 establishments (2025 annual average, per the prompt).
- Overture 2026-10-21.0: 32,020 eating and drinking listings in Massachusetts's box; the family's keep rule (Meta 0.95, or 0.90 with a
  website, or a brand feed) plus official and hand-checked places gives the App Store build **15,908 places, 15,519 restaurants**.
- Meta at 0.95+ confidence matched an official record **90.1%** of the time in Cambridge (333 listings) and **88.4%** in Somerville (225);
  Meta 0.90 with a website 43.8% and 64.0%; other sources 15-39%.
- Coverage: 47.6% of Cambridge's 780 current places to eat and 41.2% of Somerville's 575 records were found among the open map listings
  (both lists include cafeterias, caterers and a business's second license); 92 permit-only restaurants were added from the lists.
- No Google data at all (not even the private 2021 snapshot the older states' web builds read).

## Research sources (each place cites its own; data/research/app/*.json; all read 2026-11-06 through Claude's web fetcher)
- Tasting Table: the North Shore 3-Way (2026-10-21; Kelly's, Bill & Bob's, Londi's, Nick's, Zeno's), Boston lobster rolls (2026-07-10).
- Chowhound: Portuguese restaurants worth the trip (2025-07-05), Massachusetts's most historic restaurants (updated 2026-05-27).
- Meet Boston (the city's visitor bureau): North End Italian restaurants (2026-02-26), date ideas (2026-01-21, the cannoli stops), its
  current Chinatown restaurant guide.
- Cape Cod Chamber of Commerce: the lobster roll debate (2025-07-08) and its listings (Captain Frosty's, Spanky's, Arnold's).
- Discover Central Massachusetts: Worcester legacy businesses (2026-07-19). North of Boston: Cape Ann (2026-08-08, Woodman's).
- WBSM: Avo's Feast's Portuguese steak chow mein (2026-02-13).
- guide.michelin.com: MICHELIN Guide Boston's 26 Massachusetts places (and four restaurant pages for addresses).
- jamesbeard.org: 2026 semifinalists, nominees and winners; 2025 semifinalists, nominees and winners; 2025 America's Classics.
- Not usable: visitma.com (the state tourism office: a Cloudflare challenge for scripts and the fetcher), boston.com,
  bostonmagazine.com, bostonglobe.com, eater.com, wbur.org, masslive.com, patriotledger.com, capecodtimes.com, southcoasttoday.com,
  heraldnews.com (robots.txt disallows Claude).
