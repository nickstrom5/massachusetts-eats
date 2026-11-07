"""Massachusetts's open official records -> data/raw/official/ (git-ignored, never public).

Checked 2026-11-06 (playbook/12-sources.md). There is no statewide inspection data or grade: each city's or town's board of health
inspects under 105 CMR 590.000. Two cities publish open data a script may read (Socrata, robots.txt allows /resource/, Crawl-delay 1):
- Cambridge (data.cambridgema.gov, Open Data Commons PDDL): "Sanitary Inspections" (ryb9-qzmw), one row per citation, and one row with
  no code for an inspection that found none (City of Cambridge Inspectional Services Department); "Food Establishment Permits"
  (iect-ma2e), read without applicant_name or the legal business_name's owner fields (only the dba is ever shown).
- Somerville (data.somervillema.gov, ODbL, SomerStat): "Applications for Permits and Licenses" (nneb-s3f7), its active Food
  Establishment (Food Service), Common Victualer and Restaurant (with alcohol) records; no applicant or contractor fields are read.
Boston's ISD inspections and licenses (data.boston.gov, PDDL) are behind a Cloudflare Turnstile check for scripted clients (403,
"Turnstile verification required", 2026-11-06), and robots.txt disallows /api/ and /datastore/: not read, never bypassed (Nick's call).
One request at a time, at least 1.2 s apart.
"""
import datetime, json, os, time
import requests

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "official")
UA = "BayStateEatsDataCheck/1.0 (+https://nickstrom5.github.io/massachusetts-eats/; nick@eatsranked.com)"
S = requests.Session(); S.headers["User-Agent"] = UA


def soda(host, view, select=None, where=None, page=50000):
    rows, off = [], 0
    while True:
        params = {"$limit": page, "$offset": off, "$order": ":id"}
        if select:
            params["$select"] = select
        if where:
            params["$where"] = where
        for attempt in range(4):
            r = S.get(f"https://{host}/resource/{view}.json", params=params, timeout=120)
            if r.status_code == 200:
                break
            time.sleep(5 * (attempt + 1))
        r.raise_for_status()
        got = r.json()
        rows += got
        time.sleep(1.2)
        if len(got) < page:
            return rows
        off += page


def meta_of(host, view):
    d = S.get(f"https://{host}/api/views/{view}.json", timeout=60).json()
    time.sleep(1.2)
    return {"name": d.get("name"), "license": (d.get("license") or {}).get("name"),
            "rows_updated": datetime.datetime.fromtimestamp(d.get("rowsUpdatedAt", 0), datetime.timezone.utc).date().isoformat(),
            "attribution": d.get("attribution"), "url": f"https://{host}/d/{view}"}


today = datetime.date.today().isoformat()
meta = {}
for d_ in ("cambridge", "somerville"):
    os.makedirs(os.path.join(OUT, d_), exist_ok=True)

CAM = "data.cambridgema.gov"
ins = soda(CAM, "ryb9-qzmw", select="id,full_address,business_name,code_number,code_description,case_open_date,case_closed_date,"
                                    "date_corrected,status,latitude,longitude,permit_type")
per = soda(CAM, "iect-ma2e", select="id,full_address,latitude,longitude,status,issue_date,dba,permit_type,food_est_permit_type,"
                                    "number_of_seats,serving_catering")
json.dump(ins, open(os.path.join(OUT, "cambridge", "inspections.json"), "w"))
json.dump(per, open(os.path.join(OUT, "cambridge", "permits.json"), "w"))
meta["cambridge_inspections"] = {**meta_of(CAM, "ryb9-qzmw"), "fetched": today}
meta["cambridge_permits"] = {**meta_of(CAM, "iect-ma2e"), "fetched": today}
print("Cambridge inspection rows:", len(ins), "| permits:", len(per))

SOM = "data.somervillema.gov"
som = soda(SOM, "nneb-s3f7", select="application_number,application_type,application_subtype,status,project_description_or_business_name,"
                                    "application_date,issue_date,expiration_date,application_address,application_latitude,"
                                    "application_longitude,currently_active",
           where="currently_active=1 AND (application_type in ('Food Establishment', 'Common Victualer (without alcohol)', "
                 "'Restaurant (with alcohol)'))")
json.dump(som, open(os.path.join(OUT, "somerville", "permits.json"), "w"))
meta["somerville"] = {**meta_of(SOM, "nneb-s3f7"), "fetched": today}
print("Somerville active food and restaurant records:", len(som))
json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
