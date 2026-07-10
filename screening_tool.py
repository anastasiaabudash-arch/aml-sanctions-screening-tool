"""
AML Sanctions Screening Tool
Checks names/companies against OFAC SDN, EU Consolidated, and UN Sanctions lists.
Author: Portfolio Project | AML/KYC Compliance
"""

import csv
import re
import json
import urllib.request
import urllib.error
from datetime import datetime
from difflib import SequenceMatcher


# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────

FUZZY_THRESHOLD = 0.70   # Minimum score for "Possible Match"
EXACT_THRESHOLD = 0.88   # Minimum score for "Confirmed Match"

# Public sanctions list sources
SOURCES = {
    "OFAC SDN": "https://www.treasury.gov/ofac/downloads/sdn.csv",
    "EU Consolidated": "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content",
    "UN Sanctions": "https://scsanctions.un.org/resources/xml/en/consolidated.xml",
}

# Built-in demo list of sanctioned entities
DEMO_SANCTIONED_NAMES = [
    "Vladimir Vladimirovich Putin",
    "Sergei Lavrov",
    "Igor Sechin",
    "Gennady Timchenko",
    "Arkady Rotenberg",
    "Boris Rotenberg",
    "Alisher Usmanov",
    "Roman Abramovich",
    "Gazprom",
    "Rosneft",
    "Sberbank",
    "VTB Bank",
    "Kim Jong Un",
    "Iranian Revolutionary Guard Corps",
    "Hamas",
    "Hezbollah",
    "Wagner Group",
]


# ─────────────────────────────────────────────
#  CORE FUNCTIONS
# ─────────────────────────────────────────────

def normalize(name: str) -> str:
    """Lowercase, strip punctuation, collapse spaces."""
    name = name.lower().strip()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name


def similarity(a: str, b: str) -> float:
    """Fuzzy similarity ratio between two strings."""
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def check_name(query: str, sanctioned_list: list) -> dict:
    """
    Check a single name/entity against the sanctioned list.
    Returns the best match with score and verdict.
    """
    best_score = 0.0
    best_match = ""

    for entry in sanctioned_list:
        score = similarity(query, entry)
        if score > best_score:
            best_score = score
            best_match = entry

    if best_score >= EXACT_THRESHOLD:
        verdict = "CONFIRMED MATCH"
        flag = "RED"
    elif best_score >= FUZZY_THRESHOLD:
        verdict = "POSSIBLE MATCH"
        flag = "YELLOW"
    else:
        verdict = "CLEAR"
        flag = "GREEN"

    return {
        "query": query,
        "best_match": best_match if best_score >= FUZZY_THRESHOLD else "—",
        "score": round(best_score, 3),
        "verdict": verdict,
        "flag": flag,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def load_demo_list() -> list:
    """Return the built-in demo list of sanctioned entities."""
    return DEMO_SANCTIONED_NAMES


def fetch_ofac_sdn(max_entries: int = 500) -> list:
    """
    Attempt to fetch OFAC SDN list from the public URL.
    Falls back to demo list on network error.
    """
    url = SOURCES["OFAC SDN"]
    print(f"  Fetching OFAC SDN list from {url}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            lines = response.read().decode("latin-1").splitlines()

        names = []
        reader = csv.reader(lines)
        for row in reader:
            if len(row) > 1:
                name = row[1].strip()
                if name and name != "Last Name":
                    names.append(name)
            if len(names) >= max_entries:
                break
        print(f"  Loaded {len(names)} names from OFAC SDN.")
        return names
    except Exception as e:
        print(f"  Could not fetch live OFAC list ({e}). Using demo list.")
        return load_demo_list()


def screen_list(names: list, sanctioned_list: list, source_label: str = "Demo List") -> list:
    """Screen a list of names and return results."""
    results = []
    for name in names:
        result = check_name(name, sanctioned_list)
        result["source"] = source_label
        results.append(result)
    return results


def print_results(results: list) -> None:
    """Print screening results to console in a readable format."""
    print("\n" + "=" * 70)
    print(f"{'SCREENING RESULTS':^70}")
    print("=" * 70)
    print(f"{'NAME':<28} {'VERDICT':<20} {'SCORE':<8} {'BEST MATCH'}")
    print("-" * 70)

    icons = {"RED": "[RED]   ", "YELLOW": "[YELLOW]", "GREEN": "[GREEN] "}

    for r in results:
        icon = icons.get(r["flag"], "")
        print(f"{r['query']:<28} {icon} {r['verdict']:<12} {r['score']:<8} {r['best_match']}")

    print("=" * 70)

    confirmed = sum(1 for r in results if r["flag"] == "RED")
    possible = sum(1 for r in results if r["flag"] == "YELLOW")
    clear = sum(1 for r in results if r["flag"] == "GREEN")

    print(f"\nSUMMARY: {len(results)} entities screened")
    print(f"  [RED]    Confirmed Matches : {confirmed}")
    print(f"  [YELLOW] Possible Matches  : {possible}")
    print(f"  [GREEN]  Clear             : {clear}")
    print(f"\nScreened at : {results[0]['timestamp'] if results else '—'}")
    print(f"Source      : {results[0].get('source', '—')}\n")


def export_to_csv(results: list, filename: str = "screening_results.csv") -> None:
    """Export results to CSV file."""
    if not results:
        return
    keys = ["timestamp", "query", "verdict", "flag", "score", "best_match", "source"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results exported to: {filename}")


def export_to_json(results: list, filename: str = "screening_results.json") -> None:
    """Export results to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results exported to: {filename}")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    print("\n" + "=" * 70)
    print("  AML SANCTIONS SCREENING TOOL")
    print("  Checks names against OFAC SDN / EU / UN Sanctions lists")
    print("=" * 70)

    # Names to screen — edit this list as needed
    names_to_screen = [
        "Vladimir Putin",           # should match (short form)
        "Roman Abramovich",         # should match (exact)
        "Igor Sechin",              # should match (exact)
        "Gazprom OAO",              # should match (fuzzy)
        "John Smith",               # should be clear
        "Anna Kowalski",            # should be clear
        "Sber Bank Russia",         # possible match (fuzzy)
        "Kim Jong-un",              # should match (fuzzy)
        "Hezbollah Organization",   # possible match
        "Microsoft Corporation",    # should be clear
    ]

    # Load sanctioned list (demo mode — no internet required)
    sanctioned_list = load_demo_list()
    source_label = "Demo List (built-in)"

    # Uncomment to use live OFAC data:
    # sanctioned_list = fetch_ofac_sdn()
    # source_label = "OFAC SDN (live)"

    print(f"\nLoaded {len(sanctioned_list)} sanctioned entities from: {source_label}")
    print(f"Screening {len(names_to_screen)} entities...\n")

    results = screen_list(names_to_screen, sanctioned_list, source_label)
    print_results(results)
    export_to_csv(results)
    export_to_json(results)


if __name__ == "__main__":
    main()
