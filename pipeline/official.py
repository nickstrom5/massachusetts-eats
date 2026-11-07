"""Official records for Massachusetts -> one table of licensed food businesses (playbook/12-sources.md).

Massachusetts has no statewide inspection data and no official grade: each city's or town's board of health inspects under
105 CMR 590.000 (the state Food Code). Two cities publish open records a script may read (fetch_official.py):
- Cambridge: Food Establishment Permits (the dba only; never the applicant or legal name) and Sanitary Inspections, one row per
  citation and a row with no code for an inspection that found none. Shown as the city publishes it: the inspection's date, and
  either "No violations cited" or "Violations cited" with the codes. Never a grade or a score.
- Somerville: its active Food Establishment (Food Service) permits, Common Victualer licenses and "Restaurant (with alcohol)"
  licenses (that one is the only alcohol record here: "Serves alcohol" is known in Somerville only, unknown elsewhere).
Boston's ISD inspections and licenses are behind a bot check for scripts (fetch_official.py): linked, never read.

load() returns: jur, lic (our id), name, keys (name keys), addr, city, zip, num, street, lat, lon, kind, active, ltype, insp, biz.
"""
import os, re, json, datetime
import numpy as np, pandas as pd
from common import norm_name, RAW, name_sim, _stems, GENERIC, canon_city

OFF = os.path.join(RAW, "official")
DIRS = {"N": "N", "S": "S", "E": "E", "W": "W", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
TYPES = set("ST STREET AVE AV AVENUE BLVD BOULEVARD RD ROAD DR DRIVE LN LANE CT COURT PL PLACE PKWY PARKWAY TER TRL TRAIL WAY HWY CIR "
            "CIRCLE PLZ SQ MALL BND PASS XING RUN ROW WALK RDG LOOP FWY FREEWAY EXPY EXPRESSWAY PIKE PK PKE".split())


def road(a):
    """One spelling for numbered roads. Massachusetts writes one road as 'Route 100', 'US 7', 'Rt 2', 'MA 100' or 'MA Route 100', so every
    numbered US or state route is 'SH n' (as in ri-eats); 'N INTERSTATE 95' = 'I-95'; 'COUNTY ROAD 5' = 'CR 5'."""
    a = re.sub(r"(\d)\s*&\s*(\d)", r"\1-\2", a.upper())
    a = re.sub(r"\b(US|MA|SR|SH|CR|I|IH|RT|RTE)-(\w)", r"\1 \2", a)
    a = re.sub(r"\b(?:INTERSTATE(?: HIGHWAY| HWY)?|IH|I H)\s*(?=\d)", "I ", a)
    a = re.sub(r"\b(?:US|U S)\s+(?:HIGHWAY|HWY)\b", "US", a)
    a = re.sub(r"\b(?:FARM[- ]TO[- ]MARKET(?: ROAD| RD)?|FARM (?:ROAD|RD)|F M)\b", "FM", a)
    a = re.sub(r"\b(?:RANCH[- ]TO[- ]MARKET(?: ROAD| RD)?|RANCH (?:ROAD|RD)|RR|RM)\b(?=\s*\d)", "RM", a)
    a = re.sub(r"\b(?:STATE (?:HIGHWAY|HWY|ROAD|RD|ROUTE|RTE)|SR|SH|VERMONT (?:ROUTE|RTE|HIGHWAY|HWY)|MA (?:ROUTE|RTE|RT|HIGHWAY|HWY)|MA|"
               r"US (?:ROUTE|RTE|RT)|US|ROUTE|RTE|RT|HWY)\b\.?(?=\s*\d)", "SH", a)
    a = re.sub(r"\b(?:COUNTY (?:HIGHWAY|HWY|ROAD|RD)|CO RD|CTY (?:HWY|RD)|CR)\b", "CR", a)
    a = re.sub(r"\bHIGHWAY\b", "HWY", a)
    return re.sub(r"\b(US|SH|CR|HWY|FM|RM|I) (\w+)\s*-\s*\w+", r"\1 \2", a)


ORD = {"FIRST": "1ST", "SECOND": "2ND", "THIRD": "3RD", "FOURTH": "4TH", "FIFTH": "5TH", "SIXTH": "6TH", "SEVENTH": "7TH",
       "EIGHTH": "8TH", "NINTH": "9TH", "TENTH": "10TH", "ELEVENTH": "11TH", "TWELFTH": "12TH"}


def street_key(a):
    """'2505 Monroe St' -> ('2505', 'MONROE'); '1000 OSAGE STREET' -> ('1000', 'OSAGE'); 'E Colfax Ave' keeps 'COLFAX'."""
    if not isinstance(a, str):
        return None, None
    a = re.sub(r"[.,#]", " ", road(a))
    # "20940-A North Frederick Ave": a hyphenated unit letter is part of the number (Maryland's Montgomery County wrote them so)
    m = re.match(r"^\s*(\d+)(?:-?[A-Z])?(?:\s*-\s*\d+[A-Z]?)?\s+(.*)$", a)
    if not m:
        return None, None
    words = [w for w in m.group(2).split() if w]
    if len(words) > 1 and words[0] in DIRS:
        words = words[1:]
    core = []
    for w in words:
        if w in TYPES and core:
            break
        core.append(w)
    core = [ORD.get(w, w) for w in core]
    return m.group(1), " ".join(core[:3]) or None


def street_compat(a, b):
    """Same street, or one is a whole-word prefix of the other: Boulder's 2025 set sometimes truncates ("1206 CENTAUR" = Centaur Village Dr)."""
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return False
    return a == b or a.startswith(b + " ") or b.startswith(a + " ")


def street_nums(a):
    """'157-159 W Main St' -> {'157', '159'}; '2505 Monroe St' -> {'2505'}."""
    if not isinstance(a, str):
        return set()
    a = road(a)
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*(\d+)[A-Z]?)?\s", a.upper() + " ")
    if not m:
        return set()
    lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
    if hi < lo:   # "1500-02"
        hi = int(str(lo)[: len(str(lo)) - len(m.group(2))] + m.group(2)) if m.group(2) else lo
    return {str(x) for x in range(lo, hi + 1, 2 if (hi - lo) % 2 == 0 else 1)} if 0 <= hi - lo <= 12 else {str(lo)}


def _names(*vals):
    out = []
    for v in vals:
        if not isinstance(v, str):
            continue
        v = re.sub(r"\s*\((?:MOBILE|MOBILE UNIT|COMMISSARY|CATERING|SPECIAL EVENT|SPEC EVENT|TEMP(?:ORARY)? EVENT|CP|INSIDE [^)]*)\)\s*$", "", v, flags=re.I)
        for part in re.split(r"\s*/\s*|\s+\bdba\b\s+|\s+&\s+(?=[A-Z][a-z])", v, flags=re.I):
            k = norm_name(re.sub(r"\b(?:LLC|INC|CORP|CORPORATION|LTD|CO)\b\.?", "", part, flags=re.I))
            if k and k not in out:
                out.append(k)
    return out


META = json.load(open(os.path.join(OFF, "meta.json"))) if os.path.exists(os.path.join(OFF, "meta.json")) else {}
# the day of each list's own last update (Socrata's rowsUpdatedAt), never the build day
LIST_DATE = max([(META.get(k) or {}).get("rows_updated") or "" for k in ("cambridge_permits", "somerville")] or [""]) or None
# Cambridge's inspections page (the dataset; its viewer renders), and Boston's own search for its inspections (linked, never read)
MONT_PAGE = "https://data.cambridgema.gov/Inspectional-Services/Sanitary-Inspections/ryb9-qzmw"
INSPECTIONS_URL = "https://www.boston.gov/departments/inspectional-services/mayors-food-court"
# the results as the cities word them (Cambridge's dataset: an inspection either found no violations or cited some)
RESULTS = ("No violations cited", "Violations cited")
ONPREM_T = ("Somerville Restaurant (with alcohol) license",)


def liq_kind(t):
    """A license type as shown -> on-premises or retail."""
    if not isinstance(t, str):
        return None
    return "onprem" if t in ONPREM_T else "retail" if "Package" in t else None


COLUMNS = ["jur", "lic", "name", "dba", "holder", "keys", "addr", "city", "zip", "num", "street", "lat", "lon", "kind", "active", "ltype",
           "insp", "issued", "biz", "drinks", "county"]


def _zip(z):
    z = re.sub(r"\D", "", str(z or ""))
    return z[:5] if len(z) >= 5 else ""


def _addr(a):
    """'2790 VETERANS MEMORIAL BLVD STE 130' -> '2790 Veterans Memorial Blvd Ste 130'."""
    a = re.sub(r"\s+", " ", a or "").strip()
    return re.sub(r"\b([A-Z]{2,})\b", lambda m: m.group(1).title(), a)


def _day(v):
    return v[:10] if isinstance(v, str) and re.match(r"\d{4}-\d{2}-\d{2}", v) else None


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _split_addr(full):
    """'955 Massachusetts Ave, Cambridge, MA 02139' -> ('955 Massachusetts Ave', '02139')."""
    full = (full or "").strip()
    m = re.match(r"^(.*?),\s*(?:Cambridge|Somerville)\b.*?(\d{5})?\s*$", full, flags=re.I)
    return (_addr(m.group(1)), m.group(2) or "") if m else (_addr(full), "")


# Cambridge's permit kinds that are a place to eat or drink; retail, package, wholesale, daycare and institution permits stay out
CAM_FOOD = {"Non Alcohol", "Alcohol", "Bakery"}
CAM_ACTIVE_SINCE = "2025-07-01"   # permits are yearly: one issued in the last ~16 months is the current one


def load_cambridge():
    P = json.load(open(os.path.join(OFF, "cambridge", "permits.json")))
    latest = {}
    for p in P:
        dba = re.sub(r"\s+", " ", p.get("dba") or "").strip()
        if not re.search(r"[A-Za-z]{2}", dba):   # "1/5/2025" in the dba field is no name
            continue
        addr, z = _split_addr(p.get("full_address"))
        key = (norm_name(dba), street_key(addr))
        if key not in latest or (p.get("issue_date") or "") > (latest[key].get("issue_date") or ""):
            latest[key] = {**p, "_dba": dba, "_addr": addr, "_zip": z}
    rows = []
    for (k, sk), p in latest.items():
        num, st = street_key(p["_addr"])
        kind = "food" if p.get("food_est_permit_type") in CAM_FOOD else "other"
        rows.append({"jur": "cambridge", "lic": "cambridge-" + str(p.get("id")), "name": p["_dba"], "dba": p["_dba"], "holder": None,
                     "keys": _names(p["_dba"]), "addr": p["_addr"], "city": "Cambridge", "zip": p["_zip"], "num": num, "street": st,
                     "lat": _f(p.get("latitude")), "lon": _f(p.get("longitude")), "kind": kind,
                     "active": (p.get("issue_date") or "") >= CAM_ACTIVE_SINCE,
                     "ltype": "Cambridge food establishment permit (" + (p.get("food_est_permit_type") or "food") + ")",
                     "insp": [], "issued": _day(p.get("issue_date")), "drinks": None, "county": "Middlesex County"})
    # inspections: one case per inspection; a case with no code is an inspection that cited nothing. A case without an inspection
    # date (Cambridge leaves some blank) can't be dated, so it isn't shown. Joined to a permit at the same house number and street
    # whose name agrees, else the only permit of that name in the city
    cases = {}
    for r in json.load(open(os.path.join(OFF, "cambridge", "inspections.json"))):
        d = _day(r.get("case_open_date"))
        if not d or not r.get("id"):
            continue
        c = cases.setdefault(r["id"], {"date": d, "name": re.sub(r"\s+", " ", r.get("business_name") or "").strip(),
                                       "addr": _split_addr(r.get("full_address"))[0], "codes": set()})
        if (r.get("code_number") or "").strip():
            c["codes"].add(re.sub(r"[\s\xa0]+", " ", r["code_number"]).strip())
    by_addr, by_name = {}, {}
    for i, r in enumerate(rows):
        n, st = street_key(r["addr"])
        by_addr.setdefault((n, st), []).append(i)
        for k in r["keys"]:
            by_name.setdefault(k, []).append(i)
    unmatched = 0
    for cid, c in cases.items():
        ks = _names(c["name"])
        n, st = street_key(c["addr"])
        hit = None
        for i in by_addr.get((n, st), []):
            if any(name_sim(a, b) >= 80 for a in ks for b in rows[i]["keys"]) or (
                    bool(set().union(*[_stems(a) - GENERIC for a in ks] or [set()]) & set().union(*[_stems(b) - GENERIC for b in rows[i]["keys"]] or [set()]))):
                hit = i; break
        if hit is None:
            same = {i for k in ks for i in by_name.get(k, [])}
            hit = next(iter(same)) if len(same) == 1 else None
        if hit is None:
            unmatched += 1
            continue
        rows[hit]["insp"].append([c["date"], RESULTS[1] if c["codes"] else RESULTS[0], None, cid, sorted(c["codes"])])
    for r in rows:
        r["insp"].sort(key=lambda v: v[0], reverse=True)
    print("Cambridge: current permits", sum(r["active"] for r in rows), "of", len(rows), "| inspections dated", len(cases),
          "| not joined to a permit", unmatched)
    return rows


# Somerville's records that are a place to eat or drink; retail food, school kitchens, caterers, mobile units and tobacco delivery stay out
def load_somerville():
    rows = []
    for p in json.load(open(os.path.join(OFF, "somerville", "permits.json"))):
        t, sub = p.get("application_type") or "", p.get("application_subtype") or ""
        desc = (p.get("project_description_or_business_name") or "").replace("\r", "")
        first = desc.split("\n")[0].strip()
        m = re.search(r"(?i)business address:\s*([^\n]+)", desc)
        name = re.sub(r"(?i)^.*?\bd\s*/?\s*b\s*/?\s*a\b\.?:?\s+", "", first).strip(" ,")
        if not re.search(r"[A-Za-z]{2}", name):
            continue
        app_addr = _addr(re.sub(r"(?i),?\s*SOMERVILLE.*$", "", p.get("application_address") or ""))
        addr = _addr(m.group(1).strip()) if m else app_addr
        moved = bool(m) and street_key(addr) != street_key(app_addr)   # the point is the application's address, not the business's
        num, st = street_key(addr)
        food = (t == "Food Establishment" and sub == "Food Service") or t in ("Common Victualer (without alcohol)", "Restaurant (with alcohol)")
        ltype = {"Food Establishment": "Somerville food establishment permit (" + sub + ")",
                 "Common Victualer (without alcohol)": "Somerville common victualer license",
                 "Restaurant (with alcohol)": ONPREM_T[0]}.get(t, t)
        rows.append({"jur": "somerville", "lic": "somerville-" + str(p.get("application_number")), "name": name, "dba": name, "holder": None,
                     "keys": _names(name), "addr": addr, "city": "Somerville", "zip": _zip(re.search(r"\d{5}", p.get("application_address") or "") and
                                                                                            re.search(r"\d{5}", p.get("application_address")).group(0)),
                     "num": num, "street": st, "lat": None if moved else _f(p.get("application_latitude")),
                     "lon": None if moved else _f(p.get("application_longitude")), "kind": "food" if food else "other",
                     "active": (p.get("status") or "") in ("Issued", "Approved", "Renewal Required"), "ltype": ltype, "insp": [],
                     "issued": _day(p.get("issue_date")), "drinks": ["beer", "wine", "liquor"] if t == "Restaurant (with alcohol)" else None,
                     "county": "Middlesex County"})
    return rows


def load():
    """Cambridge's and Somerville's records, one row each (see the docstring)."""
    rows = []
    if os.path.exists(os.path.join(OFF, "cambridge", "permits.json")):
        rows += load_cambridge()
    if os.path.exists(os.path.join(OFF, "somerville", "permits.json")):
        rows += load_somerville()
    df = pd.DataFrame(rows) if rows else pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})
    for c_ in COLUMNS:
        if c_ not in df.columns:
            df[c_] = None
    df["lat"] = df["lat"].astype(float); df["lon"] = df["lon"].astype(float); df["active"] = df["active"].astype(bool)
    df["biz"] = np.arange(len(df))
    return df
