import json
import os
import re
import requests
from bs4 import BeautifulSoup

# Local TAC DB path
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "tac_db.json")

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

TAC_DB = load_tac_db()

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
        print(f"GSMA scrape error: {e}")
    return {}

def basic_tac_profile(identifier: str) -> dict:
    """
    Returns TAC profile from either a TAC code or a full IMEI.
    Falls back to multiple public sources if not found locally.
    """
    # Determine if input is IMEI or TAC
    if re.fullmatch(r"\d{15}", identifier):
        tac = identifier[:8]
    elif re.fullmatch(r"\d{8}", identifier):
        tac = identifier
    else:
        raise ValueError("Invalid input. Must be 8-digit TAC or 15-digit IMEI.")

    # Start with local DB
    profile = TAC_DB.get(tac, {
        "tac": tac,
        "manufacturer": "Unknown",
        "model": "Unknown",
        "region": "Unknown",
        "device_type": "Unknown",
        "release_year": "Unknown",
        "confidence": 0.0,
        "notes": ["TAC not found in local database"]
    })

    # Try GitHub TAC DB
    if profile["manufacturer"] == "Unknown":
        gh_data = fetch_tac_from_github(tac)
        if gh_data:
            profile.update({
                "manufacturer": gh_data.get("manufacturer", profile["manufacturer"]),
                "model": gh_data.get("model", profile["model"]),
                "region": gh_data.get("region", profile["region"]),
                "device_type": gh_data.get("device_type", profile["device_type"]),
                "release_year": gh_data.get("release_year", profile["release_year"]),
                "confidence": max(profile["confidence"], 0.9),
                "notes": profile["notes"] + ["Fetched from GitHub TAC database"]
            })

    # Try GSMA mirror scrape
    if profile["manufacturer"] == "Unknown" or profile["model"] == "Unknown":
        gsma_data = fetch_tac_from_gsma(tac)
        if gsma_data:
            profile.update({
                "manufacturer": gsma_data.get("manufacturer", profile["manufacturer"]),
                "model": gsma_data.get("model", profile["model"]),
                "region": gsma_data.get("country", profile["region"]),
                "device_type": gsma_data.get("device_type", profile["device_type"]),
                "release_year": gsma_data.get("release_year", profile["release_year"]),
                "confidence": max(profile["confidence"], 0.85),
                "notes": profile["notes"] + ["Fetched from GSMA TAC mirror"]
            })

    # Cache updated profile locally
    TAC_DB[tac] = profile
    save_tac_db(TAC_DB)

    return profile

# Example usage
if __name__ == "__main__":
    print(json.dumps(basic_tac_profile("35693803"), indent=2))


