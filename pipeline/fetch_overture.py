"""Download the Overture Maps extracts that massachusetts.py reads -> data/ma/

- overture_ma_bbox.parquet     every place in Massachusetts's bounding box (name, category, address, point)
- overture_ma_sources.parquet  which datasets each Massachusetts eating/drinking listing came from (Meta, Foursquare, ...)
- ma_shapes.json               simplified state and county outlines for the map
- ma_state_detail.geojson      the state outline at full detail, for the in-state test
- ma_counties_detail.geojson   the 14 counties (the files split by region; most county governments are gone, the lines remain)
- ma_towns_detail.geojson      the 351 cities and towns, the place filter: Overture's localities without the 13 Cape and other
                               villages it also lists (Hyannis, Osterville...), plus Nantucket (town = county)

Reads the public Overture bucket over S3 with DuckDB (no account needed). Ported from va-eats/pipeline/fetch_overture.py (2026-11-06).
The script checks the islands (Nantucket, Martha's Vineyard, Cuttyhunk), the Cape's tip and the towns on the lines with Rhode Island,
Connecticut, New York, Vermont and New Hampshire (Attleboro is in, Pawtucket is out; Methuen in, Salem NH out).
"""
import os, json, time
import duckdb
from shapely import wkb
from shapely.geometry import mapping, Polygon

RELEASE = "2026-10-21.0"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "ma")
# Massachusetts (41.24°N–42.89°N, 69.93°W–73.51°W) plus a margin for the border towns and the islands
BBOX = "bbox.xmin BETWEEN -73.6 AND -69.85 AND bbox.ymin BETWEEN 41.15 AND 42.95"
EAT = "('restaurant','casual_eatery','bar','fast_food_restaurant','coffee_shop','cafe','smoothie_juice_bar','brewery','food_court')"
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2';")
places = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*.parquet"

t = time.time()
if not os.path.exists(f"{OUT}/overture_ma_bbox.parquet"):
    con.execute(f"""
COPY (
  SELECT id, names.primary AS name, basic_category AS cat, taxonomy.primary AS tax, taxonomy.hierarchy AS hier, confidence,
         operating_status AS status, brand.names.primary AS brand, addresses[1].freeform AS street, addresses[1].locality AS city,
         addresses[1].postcode AS zip, addresses[1].region AS region, ST_Y(geometry) AS lat, ST_X(geometry) AS lon, websites[1] AS web,
         phones[1] AS phone
  FROM read_parquet('{places}', hive_partitioning=1) WHERE {BBOX}
) TO '{OUT}/overture_ma_bbox.parquet' (FORMAT PARQUET)""")
    print("places in bbox", round(time.time() - t), "s", flush=True)
if not os.path.exists(f"{OUT}/overture_ma_sources.parquet"):
    con.execute(f"""
COPY (
  SELECT id, list_transform(sources, lambda x: x.dataset) AS ds, list_transform(sources, lambda x: x.update_time) AS ut,
         list_transform(sources, lambda x: x.record_id) AS rid,
         len(socials) AS n_soc, len(websites) AS n_web, len(phones) AS n_ph
  FROM read_parquet('{places}', hive_partitioning=1)
  WHERE {BBOX} AND basic_category IN {EAT}
) TO '{OUT}/overture_ma_sources.parquet' (FORMAT PARQUET)""")
    print("sources", round(time.time() - t), "s", flush=True)

areas = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=divisions/type=division_area/*.parquet"
rows = con.execute(f"""
  SELECT subtype, names.primary AS name, ST_AsWKB(geometry) AS g
  FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region = 'US-MA' AND subtype IN ('region', 'county') AND class = 'land'
    AND bbox.xmin > -73.7 AND bbox.xmax < -69.8 AND bbox.ymin > 41.1 AND bbox.ymax < 43.0""").fetchall()
# Nantucket is a county and a town at once (Overture names the county "Nantucket")
rows = [(sub, "Nantucket County" if sub == "county" and name == "Nantucket" else name, g) for sub, name, g in rows]
# the 351 cities and towns: Overture's localities, less the villages it lists inside a town, plus Nantucket
VILLAGES = {"Centerville", "Cotuit", "Dennisport", "Hyannis", "Marstons Mills", "Osterville", "Pontoosuc", "Rings Island", "South Dennis",
            "Village of Barnstable", "Village of Nagog Woods", "West Barnstable", "West Dennis"}
trows = con.execute(f"""
  SELECT names.primary AS name, ST_AsWKB(geometry) AS g
  FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region = 'US-MA' AND subtype = 'locality' AND class = 'land'""").fetchall()
towns = {n: wkb.loads(bytes(g)).buffer(0) for n, g in trows if n not in VILLAGES}
towns["Nantucket"] = next(wkb.loads(bytes(g)).buffer(0) for sub, n, g in rows if n == "Nantucket County")
assert len(towns) == 351, len(towns)
json.dump({n: mapping(g.simplify(0.0002, preserve_topology=True)) for n, g in towns.items()}, open(f"{OUT}/ma_towns_detail.geojson", "w"))
print("towns:", len(towns))


def rings(geom, tol, min_area):
    geom = geom.simplify(tol, preserve_topology=True)
    polys = [p for p in getattr(geom, "geoms", [geom]) if p.geom_type == "Polygon" and p.area >= min_area]
    return [[[round(x, 3), round(y, 3)] for x, y in p.exterior.coords] for p in polys]


out = {"state": None, "counties": []}
for sub, name, g in rows:
    geom = wkb.loads(bytes(g)).buffer(0)
    if sub == "region":
        json.dump(mapping(geom.simplify(0.0005, preserve_topology=True)), open(f"{OUT}/ma_state_detail.geojson", "w"))
        out["state"] = [[r] for r in rings(geom, 0.002, 0.000005)]
    else:
        out["counties"].append({"name": name, "c": rings(geom, 0.004, 0.00002)})
# full-detail county polygons for assigning each place to a county (not shipped)
json.dump({name: mapping(wkb.loads(bytes(g)).buffer(0).simplify(0.0003, preserve_topology=True))
           for sub, name, g in rows if sub == "county"}, open(f"{OUT}/ma_counties_detail.geojson", "w"))
json.dump(out, open(f"{OUT}/ma_shapes.json", "w"), separators=(",", ":"))
print("outlines: state", len(out["state"] or []), "rings +", len(out["counties"]), "counties;", round(time.time() - t), "s total")
# islands, shores and border towns: each must fall on the right side of the detailed state outline
from shapely.geometry import shape, Point
st = shape(json.load(open(f"{OUT}/ma_state_detail.geojson")))
for nm, lon, lat, want in [("Nantucket", -70.0995, 41.2835, True), ("Siasconset", -69.9677, 41.2643, True), ("Edgartown", -70.5126, 41.3890, True),
                           ("Aquinnah", -70.7870, 41.3480, True), ("Cuttyhunk", -70.9300, 41.4250, True), ("Provincetown", -70.1860, 42.0520, True),
                           ("Chatham", -69.9600, 41.6820, True), ("Woods Hole", -70.6720, 41.5260, True), ("Block Island, RI", -71.5770, 41.1720, False),
                           ("Attleboro", -71.2856, 41.9445, True), ("Pawtucket, RI", -71.3826, 41.8787, False), ("Seekonk", -71.3370, 41.8080, True),
                           ("East Providence, RI", -71.3700, 41.8137, False), ("Fall River", -71.1550, 41.7015, True), ("Tiverton, RI", -71.2120, 41.6260, False),
                           ("Longmeadow", -72.5830, 42.0500, True), ("Enfield, CT", -72.5918, 41.9762, False), ("Great Barrington", -73.3620, 42.1960, True),
                           ("Hillsdale, NY", -73.5260, 42.1790, False), ("Williamstown", -73.2040, 42.7120, True), ("Pownal, VT", -73.2350, 42.7660, False),
                           ("Methuen", -71.1910, 42.7262, True), ("Salem, NH", -71.2009, 42.7884, False), ("Salisbury Beach", -70.8170, 42.8370, True),
                           ("Seabrook, NH", -70.8710, 42.8950, False), ("Tyngsborough", -71.4240, 42.6770, True), ("Nashua, NH", -71.4676, 42.7654, False),
                           ("Boston Common", -71.0656, 42.3550, True), ("Logan Airport", -71.0096, 42.3656, True)]:
    ok = st.contains(Point(lon, lat))
    print(f"  {nm}: {'inside' if ok else 'outside'}{'' if ok == want else '  <-- WRONG'}")
print("counties:", len(out["counties"]), sorted(c["name"] for c in out["counties"]))

# the neighbours' land (Rhode Island, Connecticut, New York, Vermont, New Hampshire): listings.py widens Massachusetts's outline ~300 m
# for shores, but only where no neighbour's land is, so a Pawtucket or Salem, NH listing on the far side of the line stays out
nb = con.execute(f"""
  SELECT region, ST_AsWKB(geometry) FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region IN ('US-RI', 'US-CT', 'US-NY', 'US-VT', 'US-NH') AND subtype = 'region' AND class = 'land'""").fetchall()
from shapely.ops import unary_union
from shapely.geometry import box
near = box(-73.7, 41.1, -69.8, 43.0)
nbg = unary_union([wkb.loads(bytes(g)).buffer(0).intersection(near) for _, g in nb])
json.dump(mapping(nbg.simplify(0.0002, preserve_topology=True)), open(f"{OUT}/ma_neighbors.geojson", "w"))
print("neighbours:", sorted(r for r, _ in nb))
