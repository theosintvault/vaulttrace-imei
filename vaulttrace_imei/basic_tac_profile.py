import json
import os
import re
import sys
import requests
from bs4 import BeautifulSoup

# Local TAC DB path (stored in same folder as this script)
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "tac_db.json")

# ---------------- Database Helpers ---------------- #

def load_tac_db():
    """Load TAC database from local file."""
    if not os.path.exists(LOCAL_DB_PATH):
        return {}
    try:
        with open(LOCAL_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading TAC database: {e}")
        return {}

def save_tac_db(db):
    """Save TAC database to local file."""
    try:
        with open(LOCAL_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
    except OSError as e:
        print(f"Error saving TAC database: {e}")

# Load DB into memory
TAC_DB = load_tac_db()

# ---------------- Fetch from GitHub ---------------- #

def fetch_tac_from_github(tac: str) -> dict:
    """Fetch TAC details from public GitHub TAC database."""
    try:
        url = f"https://raw.githubusercontent.com/MoazEb/tac-database/main/tac/{tac}.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        print(f"GitHub TAC fetch error: {e}")
    return {}

# ---------------- Fetch from GSMA ---------------- #

def fetch_tac_from_gsma(tac: str) -> dict:
    """
    Scrape TAC details from a GSMA TAC allocation mirror (HTML).
    This avoids API keys and uses public data.
    """
    try:
        url = f"https://www.imei.info/tac/{tac}/"
        r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return {}
        soup = BeautifulSoup(r.text, "html.parser")
        data = {}
        table = soup.find("table")
        if table:
            for row in table.find_all("tr"):
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                if len(cols) == 2:
                    key, value = cols
                    data[key.lower().replace(" ", "_")] = value
        return data
    except requests.RequestException as e:
        print(f"GSMA TAC fetch error: {e}")
    return {}

# ---------------- Main Lookup Logic ---------------- #

def lookup_tac(imei: str) -> dict:
    """Main lookup logic: local DB → GitHub → GSMA."""
    if not re.fullmatch(r"\d{15}", imei):
        return {"error": "Invalid IMEI format. Must be 15 digits."}

    tac = imei[:8]

    # 1. Check local DB
    if tac in TAC_DB:
        return {"TAC": tac, **TAC_DB[tac]}

    # 2. Try GitHub
    gh_data = fetch_tac_from_github(tac)
    if gh_data:
        TAC_DB[tac] = gh_data
        save_tac_db(TAC_DB)
        return {"TAC": tac, **gh_data}

    # 3. Try GSMA scraping
    gsma_data = fetch_tac_from_gsma(tac)
    if gsma_data:
        TAC_DB[tac] = gsma_data
        save_tac_db(TAC_DB)
        return {"TAC": tac, **gsma_data}

    # 4. Not found anywhere
    return {"TAC": tac, "brand": "Unknown", "model": "Unknown", "type": "Unknown"}

# ---------------- CLI Entry Point ---------------- #

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m vaulttrace_imei.basic_tac_profile <IMEI>")
        sys.exit(1)

    imei_input = sys.argv[1]
    result = lookup_tac(imei_input)

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"TAC: {result['TAC']}")
        print(f"Brand: {result.get('brand', 'Unknown')}")
        print(f"Model: {result.get('model', 'Unknown')}")
        print(f"Type: {result.get('type', 'Unknown')}")


