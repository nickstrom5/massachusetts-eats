"""Writes data/research/app/*.json (hand-checked Massachusetts guides), data/research/michelin.json, jbf.json and closed.json from the
compact lists below. Ported from wy-eats/pipeline/build_research.py.

Each entry cites the page that names it, read on 2026-11-06 through Claude's web fetcher (every host's robots.txt lets Claude read it;
check_sources.py): Tasting Table and Chowhound's dated articles, the official visitor bureaus' guides and listings (Meet Boston, the
Cape Cod Chamber of Commerce, Discover Central Massachusetts, North of Boston), WBSM, jamesbeard.org and guide.michelin.com. The address
comes from the map listing we already hold for that name in that town (site/massachusetts.json); a name that isn't found exactly once
in its town (or at the street number given) is left out and listed in data/research/app/LEADS.md. Towns are the 351 cities and towns:
Hyannis is Barnstable, Charlestown is Boston, Vineyard Haven is Tisbury.
Usage: ../.venv/bin/python build_research.py   (then massachusetts.py)"""
import json, os, re
from brands import brand_of
from common import norm_name
ROOT = os.path.join(os.path.dirname(__file__), "..")
R = os.path.join(ROOT, "data", "research")
d = json.load(open(os.path.join(ROOT, "site", "massachusetts.json")))
C, M = d["cols"], d["meta"]
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower().replace("'", "").replace("’", ""))).strip()

# each dated on its face, or an official visitor bureau's current guide or listing (read 2026-11-06)
TT_BEEF = "https://www.tastingtable.com/2291004/north-shore-three-way-roast-beef-sandwich-toppings-bun/"   # 2026-10-21
TT_LOB = "https://www.tastingtable.com/2208179/best-lobster-rolls-boston/"                                 # 2026-07-10
CCC_LOB = "https://www.capecodchamber.org/articles/stories/post/the-great-cape-cod-lobster-roll-debate/"   # 2025-07-08
CCC = lambda slug: f"https://www.capecodchamber.org/listing/{slug}/"                                     # Cape Cod Chamber listing
NOB_CA = "https://northofboston.org/blog/discover-things-to-do-in-cape-ann/"                               # 2026-08-08
MB_NE = "https://www.meetboston.com/blog/post/italian-restaurants-in-bostons-north-end/"                   # 2026-02-26
MB_DATE = "https://www.meetboston.com/blog/post/date-ideas-in-boston/"                                     # 2026-01-21
MB_CT = "https://www.meetboston.com/explore/neighborhoods/theater-district-chinatown/chinatown-restaurants/"  # Meet Boston's guide (2026)
DCMA = "https://www.discovercentralma.org/articles/post/legacy-businesses-of-worcester/"                  # 2026-07-19
CH_PORT = "https://www.chowhound.com/1899180/must-try-portuguese-restaurants-in-united-states"              # 2025-07-05
WBSM_AVO = "https://wbsm.com/fall-river-portuguese-steak-chow-mein/"                                       # 2026-02-13
CH_HIST = "https://www.chowhound.com/1855730/most-historic-restaurants-massachusetts/"                      # updated 2026-05-27
JBF26 = "https://www.jamesbeard.org/stories/james-beard-award-semifinalists-2026"                         # 2026-01-21
JBF25 = "https://www.jamesbeard.org/stories/the-2025-james-beard-award-semifinalists"                     # 2025-01-22
JBF25N = "https://www.jamesbeard.org/stories/2025-james-beard-awards-restaurant-and-chef-nominees"        # 2025-04-02
JBF25C = "https://www.jamesbeard.org/stories/announcing-the-2025-restaurant-and-chef-americas-classics-winners"  # 2025-02-26
MI_MA = "https://guide.michelin.com/us/en/massachusetts/restaurants"                                      # read 2026-11-06
HIST_N = "Chowhound's most historic Massachusetts restaurants (May 2026)"

# (name as the source writes it or as our listing spells it, town as our listing has it, street number to pick the location (or
# None), note, founded, founded_note, [sources])
GUIDES = {
 "roast beef": [   # Tasting Table's North Shore 3-Way article (October 2026): the shops it names
  ("Kelly's Roast Beef", "Revere", "410", "The Revere Beach stand credited with inventing the North Shore 3-Way (sauce, mayo, cheese) in 1951.",
   1951, "Tasting Table (October 2026): the 3-Way was invented at Kelly's on Revere Beach in 1951.", [TT_BEEF]),
  ("Bill & Bob's Roast Beef", "Salem", None, "The Salem shop where James River barbecue sauce went on the sandwich.", None, None, [TT_BEEF]),
  ("Londi's", "Peabody", None, "A North Shore roast beef and pizza shop on Tasting Table's 3-Way list.", None, None, [TT_BEEF]),
  ("Nicks Roast Beef", "Beverly", "139", "Beverly's roast beef counter, on Tasting Table's 3-Way list.", None, None, [TT_BEEF]),
  ("Zeno's", "Ipswich", None, "An Ipswich roast beef shop on Tasting Table's 3-Way list.", None, None, [TT_BEEF])],
 "clam shack": [   # Boston's lobster rolls (Tasting Table, July 2026), the Cape's (Cape Cod Chamber, July 2025), Essex's fried clams
  ("Boston Sail Loft", "Boston", "80", "A warm buttered lobster roll on brioche, with a cup of butter on the side, on the harbor.", None, None, [TT_LOB]),
  ("Row 34", "Boston", "383", "Warm buttered and creamy (Ethel's) lobster rolls at the Fort Point oyster bar.", None, None, [TT_LOB]),
  ("Neptune Oyster", "Boston", "63", "A North End oyster bar: the lobster roll comes hot with butter or cold with mayo. No reservations.", None, None, [TT_LOB]),
  ("James Hook & Co.", "Boston", "440", "A waterfront lobster shack: rolls hot or cold, in two sizes, with a big summer patio.", None, None, [TT_LOB]),
  ("Pauli's", "Boston", "65", "Cold lobster rolls with lemon in three sizes, up to the 28-ounce USS Lobstitution.", None, None, [TT_LOB]),
  ("Alive & Kicking Lobsters", "Cambridge", "269", "A lobster pound whose lobster sandwich comes on Scali bread with chips.", None, None, [TT_LOB]),
  ("Eventide Fenway", "Boston", "1321", "A brown-butter lobster roll near Fenway Park.", None, None, [TT_LOB]),
  ("The Lobster Pot", "Provincetown", "321", "All-knuckle lobster salad rolls on Commercial Street.", None, None, [CCC_LOB]),
  ("Arnold's Lobster & Clam Bar", "Eastham", None, "A seasonal Outer Cape clam bar: fried, steamed and baked seafood, lobster rolls cold or warm.", None, None,
   [CCC_LOB, CCC("arnolds-lobster-&-clam-bar/3702")]),
  ("Black Cat Tavern", "Barnstable", "165", "A Hyannis harbor tavern with a raw bar and a lobster salad roll.", None, None, [CCC_LOB]),
  ("Quahog Republic Dive Bar", "Falmouth", None, "Falmouth's dive bar and its \"Monsta Lobsta Roll\" with drawn butter.", None, None, [CCC_LOB]),
  ("Quahog Republic Waterfront Eatery", "Wareham", None, "The Onset Village branch, on the water, with the same Monsta Lobsta Roll.", None, None, [CCC_LOB]),
  ("The Skipper Restaurant and Chowder House", "Yarmouth", "152", "A South Yarmouth chowder house since 1936, with three lobster rolls.", 1936,
   "Cape Cod Chamber of Commerce (July 2025): established in 1936.", [CCC_LOB]),
  ("The Canteen", "Provincetown", None, "Lobster rolls warm and buttered or cold with lemon mayo, and lobster grilled cheese.", None, None, [CCC_LOB]),
  ("Mattakeese Wharf", "Barnstable", None, "A Barnstable Harbor seafood house you can reach by boat.", None, None, [CCC_LOB]),
  ("Sesuit Harbor Cafe", "Dennis", None, "A harborside lobster-roll shack at Sesuit Harbor.", None, None, [CCC_LOB]),
  ("Captain Frosty's", "Dennis", None, "A Route 6A fried-seafood stand since 1976: Chatham cod, Ipswich clams and lobster rolls.", None, None,
   [CCC("captain-frostys/3772")]),
  ("Spanky's Clam Shack", "Barnstable", None, "A Hyannis harbor clam shack: lobster dinners, fried clams, scallops and fish and chips.", None, None,
   [CCC("spankys-clam-shack-%26-seaside-saloon/2981")]),
  ("Woodman's of Essex", "Essex", None, "The Essex causeway clam shack where the fried clam was invented over 100 years ago; open year-round.", None, None, [NOB_CA]),
  ("Blue Collar Lobster / The Gloucester House Pub", "Gloucester", "63", "Lobster and calamari on the harbor; its takeout window is Blue Collar Lobster.", None, None, [NOB_CA])],
 "north end": [   # Meet Boston's North End Italian restaurants (February 2026) and its North End cannoli stops (January 2026)
  ("Libertine", "Boston", "125", "Trendy Italian with Portuguese specials and late-night food.", None, None, [MB_NE]),
  ("Antico Forno", "Boston", "93", "Neapolitan pizza and southern Italian dishes from a brick oven.", None, None, [MB_NE]),
  ("Trattoria Il Panino", "Boston", "280", "Lobster ravioli and gnocchi served in the sauté pan.", None, None, [MB_NE]),
  ("Mare", "Boston", "223", "Italian seafood and an oyster bar on Hanover Street.", None, None, [MB_NE]),
  ("Quattro", "Boston", "264", "An Italian rotisserie with handmade pasta and hand-tossed pizza.", None, None, [MB_NE]),
  ("Aqua Pazza", "Boston", "135", "A white-tablecloth seafood and oyster bar.", None, None, [MB_NE]),
  ("Limoncello", "Boston", "190", "Antipasto and house lasagna for groups and celebrations.", None, None, [MB_NE]),
  ("Cantina Italiana", "Boston", "346", "Homestyle Italian since 1931, called the oldest restaurant in the North End.", 1931,
   "Meet Boston (February 2026): founded in 1931.", [MB_NE]),
  ("Artu", "Boston", "6", "Short-rib ravioli and eggplant parm at a lively bar.", None, None, [MB_NE]),
  ("Assaggio", "Boston", "29", "Positano-style cooking: lasagna and veal parmigiana.", None, None, [MB_NE]),
  ("Bacco", "Boston", "107", "A bar-first North End spot with window seats.", None, None, [MB_NE]),
  ("Forcella", "Boston", "33", "Charcuterie and rabbit gnocchi, with a big patio on North Square.", None, None, [MB_NE]),
  ("Mamma Maria", "Boston", "3", "North Square dining rooms cooking with New England ingredients.", None, None, [MB_NE]),
  ("Ristorante Villa Francesca", "Boston", "150", "Spaghetti and meatballs a minute from the Paul Revere House.", None, None, [MB_NE]),
  ("Terramia Ristorante", "Boston", "98", "A rustic trattoria with a vegan and vegetarian menu.", None, None, [MB_NE]),
  ("Tresca", "Boston", "233", "Tuscan-inspired dishes, with a balcony.", None, None, [MB_NE]),
  ("Modern Pastry", "Boston", None, "A North End pastry shop for cannoli.", None, None, [MB_DATE]),
  ("Mike's Pastry", "Boston", None, "The Hanover Street pastry shop for cannoli.", None, None, [MB_DATE]),
  ("Bova's Bakery", "Boston", None, "A North End bakery for late cannoli.", None, None, [MB_DATE])],
 "portuguese": [
  ("Sagres", "Fall River", "177", "One of the country's first Portuguese restaurants: bife à Portuguesa, mariscada and caldo verde.", 1976,
   "Chowhound (July 2025, May 2026): opened in 1976.", [CH_PORT, CH_HIST]),
  ("Antonio's", "New Bedford", "267", "New Bedford Portuguese since 1989: lulas fritas, bitoque and the caçoila sandwich.", 1989,
   "Chowhound (July 2025): opened in 1989.", [CH_PORT]),
  ("Baleia", "Boston", "264", "A South End Portuguese restaurant (2024): shrimp Mozambique, octopus carpaccio and sonhos.", 2024,
   "Chowhound (July 2025): established in 2024.", [CH_PORT]),
  ("Avo's Feast", "Fall River", None, "Portuguese steak chow mein, a plate or a papo seco sandwich, with Fall River's own noodles.", None, None, [WBSM_AVO])],
 "classic diner": [   # Discover Central Massachusetts's Worcester legacy businesses (July 2026), and Fall River's Al Mac's (Chowhound)
  ("Miss Worcester Diner", "Worcester", "300", "A Worcester Lunch Car Company diner across from the old diner factory.", None, None, [DCMA]),
  ("Boulevard Diner", "Worcester", "155", "A Shrewsbury Street diner, a Worcester legacy business.", None, None, [DCMA]),
  ("Kenmore Diner", "Worcester", "250", "A cash-only Franklin Street diner, busy late at night and early in the morning.", None, None, [DCMA]),
  ("Parkway Diner", "Worcester", "148", "A Shrewsbury Street diner and Italian kitchen, a Worcester legacy business.", None, None, [DCMA]),
  ("Ralph's Rock Diner", "Worcester", "148", "Ralph's Chadwick Square Diner, on Grove Street at Chadwick Square.", None, None, [DCMA]),
  ("Lou Roc's Diner", "Worcester", "1074", "A West Boylston Street diner, a Worcester legacy business.", None, None, [DCMA]),
  ("Marvin's Corner Lunch", "Worcester", "131", "A Lamartine Street lunch counter, a Worcester legacy business.", None, None, [DCMA]),
  ("Al Mac's Diner", "Fall River", "135", "A 1953 diner car whose business began as a horse-drawn lunch wagon in 1910; a city landmark.", None, None, [CH_HIST])],
 "chinatown": [   # Meet Boston's Chinatown guide (2026): its dim sum houses and bakeries
  ("China Pearl Restaurant", "Boston", "9", "Dim sum by day and Cantonese banquets by night for over 40 years.", None, None, [MB_CT]),
  ("Ding Ho", "Boston", "88", "To-go dim sum, known for Cantonese rice rolls.", None, None, [MB_CT]),
  ("Dynasty", "Boston", "14A", "Dim sum made fresh every day.", None, None, [MB_CT]),
  ("Empire Garden", "Boston", "690", "Daily dim sum in the old Globe Theatre building.", None, None, [MB_CT]),
  ("Hei La Moon Restaurant", "Boston", "83", "Daily dim sum on two floors.", None, None, [MB_CT]),
  ("Jumbo Seafood Restaurant", "Boston", "5", "Cantonese seafood and dim sum.", None, None, [MB_CT]),
  ("Winsor Dim Sum Cafe", "Boston", "10", "A casual tearoom with made-to-order dim sum.", None, None, [MB_CT]),
  ("Ho Yuen Bakery", "Boston", "54", "One of Boston's last traditional Chinese bakeries.", None, None, [MB_CT]),
  ("Golden Crust Bakery", "Boston", "18", "Pineapple buns, egg tarts and milk bread.", None, None, [MB_CT]),
  ("Corner Cafe & Bakery", "Boston", "62", "Barbecue pork buns, pastries and moon cakes.", None, None, [MB_CT]),
  ("Le Cafe and Bakery", "Boston", "66", "Egg tarts and croissants.", None, None, [MB_CT])],
 "historic tavern": [   # Chowhound's most historic Massachusetts restaurants (May 2026): inns and taverns
  ("Longfellow's Wayside Inn", "Sudbury", None, "One of the country's oldest operating inns, on the old Boston Post Road, with Sunday dinners.", 1716,
   f"{HIST_N}: 1716.", [CH_HIST]),
  ("Publick House", "Sturbridge", None, "The Historic Tap Room, in the 1771 inn's original dining room.", 1771, f"{HIST_N}: 1771.", [CH_HIST]),
  ("Rye Tavern", "Plymouth", None, "A farm-to-table tavern in a 1792 building that was Cornish's Tavern.", 1792, f"{HIST_N}: 1792, as The Cornish's Tavern.", [CH_HIST]),
  ("Union Oyster House", "Boston", "41", "Called America's oldest continuously operating restaurant: oysters and chowder on the Freedom Trail.", 1826,
   f"{HIST_N}: 1826.", [CH_HIST]),
  ("Warren Tavern", "Boston", None, "A Charlestown tavern named for Dr. Joseph Warren, who died at Bunker Hill.", None, None, [CH_HIST]),
  ("Bell in Hand", "Boston", None, "A tavern founded in 1795, named for the town crier Jimmy Wilson.", None, None, [CH_HIST]),
  ("The Black Dog Tavern", "Tisbury", "20", "Martha's Vineyard's first year-round restaurant, opened January 1, 1971.", 1971, f"{HIST_N}: opened January 1, 1971.", [CH_HIST]),
  ("1761 Old Mill", "Westminster", None, "A riverside New England restaurant in a 1761 sawmill.", None, None, [CH_HIST])],
}
# places the map data doesn't show as a kept place to eat (a BrightQuery, Microsoft or Foursquare copy only, or none): the street
# address from the guide that names it (Meet Boston, Chowhound) or from the place's own map listing
ADDR = {("Mattakeese Wharf", "Barnstable"): "273 Millway", ("Baleia", "Boston"): "264 E Berkeley St",
        ("China Pearl Restaurant", "Boston"): "9 Tyler St", ("Jumbo Seafood Restaurant", "Boston"): "5 Hudson St",
        ("Le Cafe and Bakery", "Boston"): "66 Kneeland St",
        ("Marvin's Corner Lunch", "Worcester"): "131 Lamartine St", ("Longfellow's Wayside Inn", "Sudbury"): "72 Wayside Inn Rd",
        ("Publick House", "Sturbridge"): "277 Main St"}
CUISINE = {("Taiwan Bakery", "Boston"): "Bakery & Sweets", ("Le Cafe and Bakery", "Boston"): "Bakery & Sweets", ("Modern Pastry", "Boston"): "Bakery & Sweets", ("Mike's Pastry", "Boston"): "Bakery & Sweets", ("Bova's Bakery", "Boston"): "Bakery & Sweets",
           ("Avo's Feast", "Fall River"): "European", ("Baleia", "Boston"): "European",
           ("Sagres", "Fall River"): "European", ("Antonio's", "New Bedford"): "European"}
POINT = {}
DISPLAY = {}
KINDS = {k: [k] for k in GUIDES}

# MICHELIN Guide Boston (first selection November 2025): the 26 Massachusetts places on guide.michelin.com (read 2026-11-06): one
# star, six Bib Gourmands, nineteen recommended ("Selected Restaurants"). Greater Boston only.
MICHELIN = [("311 Omakase", "Boston", "1 Star", "Japanese"),
            ("Bar Volpe", "Boston", "Bib Gourmand", "Italian"), ("Fox & the Knife", "Boston", "Bib Gourmand", "Italian"),
            ("Mahaniyom", "Brookline", "Bib Gourmand", "Thai"), ("Jahunger", "Cambridge", "Bib Gourmand", "Asian"),
            ("Pagu", "Cambridge", "Bib Gourmand", "Asian"), ("Sumiao Hunan Kitchen", "Cambridge", "Bib Gourmand", "Chinese"),
            ("Urban Hearth", "Cambridge", "Recommended", "Contemporary"), ("Giulia", "Cambridge", "Recommended", "Italian"),
            ("Nightshade Noodle Bar", "Lynn", "Recommended", "Contemporary"), ("Toro", "Boston", "Recommended", "Spanish"),
            ("Moëca", "Cambridge", "Recommended", "Fish and Seafood"), ("Asta", "Boston", "Recommended", "Contemporary"),
            ("Mooncusser", "Boston", "Recommended", "Contemporary"), ("Somaek", "Boston", "Recommended", "Korean"),
            ("Wa Shin", "Boston", "Recommended", "Japanese"), ("La Padrona", "Boston", "Recommended", "Italian-American"),
            ("Lenox Sophia", "Boston", "Recommended", "Contemporary"), ("Woods Hill Pier 4", "Boston", "Recommended", "American"),
            ("Oleana", "Cambridge", "Recommended", "Middle Eastern"), ("Thistle & Leek", "Newton", "Recommended", "American"),
            ("Carmelina's", "Boston", "Recommended", "Italian-American"), ("Zhi Wei Cafe", "Boston", "Recommended", "Chinese"),
            ("Pammy's", "Cambridge", "Recommended", "Mediterranean"), ("Neptune Oyster", "Boston", "Recommended", "Fish and Seafood"),
            ("Select Oyster Bar", "Boston", "Recommended", "Fish and Seafood")]
MI_MATCH = {"Fox & the Knife": ["FOX AND THE KNIFE"], "Select Oyster Bar": ["SELECT OYSTER"], "Moëca": ["MOECA"],
            "Somaek": ["SOMAEK KOREAN"], "La Padrona": ["LA PADRONA BOSTON"]}
MI_UT = MI_MA
# James Beard (facts with sources): Massachusetts's 2025 America's Classic, its 2025 nominees and its 2025-26 semifinalists (no
# Massachusetts finalist or winner in 2026); jamesbeard.org pages read 2026-11-06
NE = "Best Chef: Northeast"
JBF = [{"name": "Sullivan's Castle Island", "city": "Boston", "honors": ["America's Classics 2025"], "sources": [JBF25C], "match_names": ["SULLIVANS"]},
       {"name": "Sarma", "city": "Somerville", "honors": ["Outstanding Chef finalist 2025 (Cassie Piuma)"], "sources": [JBF25N, JBF25]},
       {"name": "Urban Hearth", "city": "Cambridge", "honors": [f"{NE} finalist 2025 (Erin Miller)"], "sources": [JBF25N, JBF25]},
       {"name": "Merai", "city": "Brookline", "honors": ["Best New Bar finalist 2025"], "sources": [JBF25N, JBF25], "match_names": ["MERAI BAR"]},
       {"name": "O Ya", "city": "Boston", "honors": ["Outstanding Restaurant semifinalist 2026"], "sources": [JBF26]},
       {"name": "Gaaeng Supper Club", "city": "Boston", "honors": ["Emerging Chef semifinalist 2026 (Pao Thampitak)"], "sources": [JBF26]},
       {"name": "Verveine Cafe & Bakery", "city": "Cambridge", "honors": ["Outstanding Pastry Chef or Baker semifinalist 2026 (Monica Glass)"], "sources": [JBF26]},
       {"name": "Cuvée", "city": "Chatham", "honors": ["Outstanding Pastry Chef or Baker semifinalist 2026 (Whitney Stancil)"], "sources": [JBF26],
        "match_names": ["CUVEE AT CHATHAM INN", "CHATHAM INN"]},
       {"name": "Ostra", "city": "Boston", "honors": ["Outstanding Hospitality semifinalist 2026"], "sources": [JBF26]},
       {"name": "State Road", "city": "West Tisbury", "honors": ["Outstanding Hospitality semifinalist 2026"], "sources": [JBF26]},
       {"name": "Talulla", "city": "Cambridge", "honors": ["Outstanding Wine and Other Beverages Program semifinalist 2026",
                                                        f"{NE} semifinalist 2025 (Conor Dennehy)"], "sources": [JBF26, JBF25]},
       {"name": "Spoke Wine Bar", "city": "Somerville", "honors": ["Outstanding Bar semifinalist 2026"], "sources": [JBF26]},
       {"name": "Zurito", "city": "Boston", "honors": ["Outstanding Professional in Beverage Service semifinalist 2026 (Nader Asgari-Tari)"], "sources": [JBF26]},
       {"name": "The Koji Club", "city": "Boston", "honors": ["Outstanding Professional in Beverage Service semifinalist 2026 and 2025 (Alyssa Mikiko DiPasquale)"],
        "sources": [JBF26, JBF25]},
       {"name": "Comfort Kitchen", "city": "Boston", "honors": [f"{NE} semifinalist 2026 (Sāsha Coleman)", f"{NE} semifinalist 2025 (Kwasi Kwaa)"],
        "sources": [JBF26, JBF25]},
       {"name": "La Padrona", "city": "Boston", "honors": [f"{NE} semifinalist 2026 (Amarilys Colon)"], "sources": [JBF26], "match_names": ["LA PADRONA BOSTON"]},
       {"name": "Tonino", "city": "Boston", "honors": [f"{NE} semifinalist 2026 (Luke Fetbroth)"], "sources": [JBF26]},
       {"name": "Lenox Sophia", "city": "Boston", "honors": [f"{NE} semifinalist 2026 (Shi Mei)"], "sources": [JBF26]},
       {"name": "Lê Madeline", "city": "Quincy", "honors": [f"{NE} semifinalist 2026 (Peter Nguyen)"], "sources": [JBF26], "match_names": ["LE MADELINE"]},
       {"name": "MIDA", "city": "Boston", "honors": ["Outstanding Restaurateur semifinalist 2025 (Seth Gerber and Douglass Williams)"], "sources": [JBF25]},
       {"name": "LUNE", "city": "Dennis", "honors": ["Best New Restaurant semifinalist 2025"], "sources": [JBF25]},
       {"name": "Somaek", "city": "Boston", "honors": ["Best New Restaurant semifinalist 2025"], "sources": [JBF25], "match_names": ["SOMAEK KOREAN"]},
       {"name": "Equal Measure", "city": "Boston", "honors": ["Best New Bar semifinalist 2025"], "sources": [JBF25]},
       {"name": "The Wig Shop", "city": "Boston", "honors": ["Outstanding Professional in Cocktail Service semifinalist 2025 (Oscar Simoza)"], "sources": [JBF25]},
       {"name": "Chickadee", "city": "Boston", "honors": [f"{NE} semifinalist 2025 (John DaSilva)"], "sources": [JBF25]},
       {"name": "Black Cat", "city": "Boston", "honors": [f"{NE} semifinalist 2025 (Valentine Howell)"], "sources": [JBF25]},
       {"name": "Nightshade Noodle Bar", "city": "Lynn", "honors": [f"{NE} semifinalist 2025 (Rachel Miller)"], "sources": [JBF25]},
       {"name": "Select Oyster Bar", "city": "Boston", "honors": [f"{NE} semifinalist 2025 (Michael Serpa)"], "sources": [JBF25], "match_names": ["SELECT OYSTER"]}]
# closed, each with a source (none verified this pass)
CLOSED = []


def key(s):
    """The name key without a leading "the": "Varsity" is our "The Varsity"."""
    return re.sub(r"^the ", "", norm(s))


def find(name, town, num):
    k = key(name)
    hits = [i for i, n in enumerate(C["name"]) if C["city"][i] is not None and M["cities"][C["city"][i]] == town
            and (key(n) == k or key(n).startswith(k + " ") or k.startswith(key(n) + " ") or key(n).replace(" ", "") == k.replace(" ", "")
                 or (key(n).split()[:2] == k.split()[:2] and len(k.split()) >= 2))]
    if num:
        hits = [i for i in hits if (C["addr"][i] or "").split(" ")[0].upper() == num.upper()]
    exact = [i for i in hits if key(C["name"][i]) == k]   # "Limoncello" and "Limoncello Ristorante", one place listed twice
    return exact if len(hits) > 1 and len(exact) == 1 else hits


leads, n_out = [], {}
for kind, rows in GUIDES.items():
    out = []
    for name, town, num, note, founded, fnote, srcs in rows:
        hits = find(name, town, num)
        if not hits and (name, town) in ADDR:
            out.append({"name": name, "address": ADDR[(name, town)], "city": town, "zip": None, "kinds": KINDS[kind], "dishes": [], "note": note,
                        "founded": founded, "founded_note": fnote, "website": None, "open": True, "evidence_date": "2026-10",
                        "sources": srcs, "match_names": []} | ({"cuisine": CUISINE[(name, town)]} if (name, town) in CUISINE else {})
                       | ({"lat": POINT[(name, town)][0], "lon": POINT[(name, town)][1]} if (name, town) in POINT else {}))
            continue
        if len(hits) != 1:
            leads.append(f"- {kind}: {name} ({town}{', ' + num if num else ''}) — {len(hits)} matches in our data; not added"); continue
        i = hits[0]
        out.append({"name": C["name"][i], "address": C["addr"][i], "city": town, "zip": str(C["zip"][i]) if C["zip"][i] else None,
                    "kinds": KINDS[kind], "dishes": [], "note": note, "founded": founded, "founded_note": fnote, "website": None, "open": True,
                    "evidence_date": "2026-10", "sources": srcs, "match_names": [name.upper()] if norm(name) != norm(C["name"][i]) else []})
        if brand_of(norm_name(name)):   # a chain shows under its own spelling at every branch, whatever the listing says
            out[-1]["display"] = name
        if (name, town) in DISPLAY:
            out[-1]["display"] = DISPLAY[(name, town)]
        if (name, town) in CUISINE:
            out[-1]["cuisine"] = CUISINE[(name, town)]
    fn = re.sub(r"[^a-z]+", "_", kind).strip("_")
    json.dump(out, open(f"{R}/app/{fn}.json", "w"), indent=1, ensure_ascii=False)
    n_out[kind] = len(out)

# the street address from the place's own MICHELIN page (read 2026-11-06), for the four the map listings don't have as a place to eat
MI_ADDR = {"311 Omakase": "605 Tremont St", "Jahunger": "272 Brookline St", "Wa Shin": "222 Stuart St", "Zhi Wei Cafe": "104 South St"}
json.dump({"restaurants": [{"name": n, "address": MI_ADDR.get(n), "city": t, "zip": None, "distinction": dist, "cuisine": cu, "green_star": False,
                             "michelin_url": MI_UT, "sources": [MI_UT], "match_names": [x.upper() for x in MI_MATCH.get(n, [])], "open": True}
                            for n, t, dist, cu in MICHELIN]}, open(f"{R}/michelin.json", "w"), indent=1, ensure_ascii=False)
json.dump([dict({"address": None}, **j, zip=None, open=True) for j in JBF], open(f"{R}/jbf.json", "w"), indent=1, ensure_ascii=False)
json.dump(CLOSED, open(f"{R}/closed.json", "w"), indent=1, ensure_ascii=False)
open(f"{R}/app/LEADS.md", "w").write("# Massachusetts research leads (not yet verified)\n\nWritten by pipeline/build_research.py.\n\n" + "\n".join(leads) + """

## Waiting for a source we may use
- South Shore bar pizza (the Lynwood Cafe, Poopsie's, Town Spa, Alumni Cafe, Venice Cafe): no 2025-26 source on a host that lets
  Claude read it (boston.com, bostonmagazine.com, patriotledger.com and masslive.com disallow it), so the guide waits.
- Worcester diners in Central Mass outside Worcester (Brody's, Dinky's Blue Belle): Discover Central MA's diner article is from 2018.
- Fall River and New Bedford Portuguese bakeries (Lou's, Europa, Barcelos, Lorenzo's): the articles are from 2024.
- visitma.com (the state tourism office) answers scripts and the web fetcher with a Cloudflare challenge: not used.
- Taiwan Bakery (56 Beach St, Meet Boston): the map listing at that address is "101 Bakery", so it is left out until one source settles the name.
- Gaaeng Supper Club (Boston; 2026 Emerging Chef semifinalist) and Black Cat (Jamaica Plain; 2025 Best Chef: Northeast semifinalist)
  aren't in the map data and have no address on the James Beard page: not placed.
- Older James Beard honors (Ana Sortun 2005, Jamie Bissonnette 2014, Joanne Chang 2016, Karen Akunowicz 2018) wait for a jamesbeard.org
  page each.
""")
print(n_out, "| leads:", len(leads))
for l in leads: print(l)
