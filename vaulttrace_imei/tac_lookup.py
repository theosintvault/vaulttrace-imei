"""
tac_lookup.py
-------------
Public-safe TAC lookup module.

- No private TAC/device data is shipped.
- Uses public GitHub TAC DB as primary source.
- Optional full DB preload (--update-cache).
- Caches results locally in tac_db.json.
"""

import json
import os
import re
import requests
import tempfile
import zipfile
from typing import Dict, Optional

# -----------------------------
# Config
# -----------------------------
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "tac_db.json")
GITHUB_TAC_BASE = "https://raw.githubusercontent.com/MoazEb/tac-database/main/tac"
GITHUB_TAC_ZIP = "https://github.com/MoazEb/tac-database/archive/refs/heads/main.zip"
HTTP_TIMEOUT = 5  # seconds

# -----------------------------
# Local DB Handling
# -----------------------------
def load_tac_db() -> Dict[str, dict]:
    if not os.path.exists(LOCAL_DB_PATH):
        return {}
    try:
        with open(LOCAL_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def save_tac_db(db: Dict[str, dict]) -> None:
    try:
        with open(LOCAL_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
    except OSError:
        pass

TAC_DB = load_tac_db()

# -----------------------------
# Online Sources
# -----------------------------
def fetch_tac_from_github(tac: str) -> Optional[dict]:
    """Fetch TAC details from public GitHub TAC DB."""
    try:
        url = f"{GITHUB_TAC_BASE}/{tac}.json"
        r = requests.get(url, timeout=HTTP_TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None

# -----------------------------
# Main Lookup
# -----------------------------
def basic_tac_profile(identifier: str) -> dict:
    """Return TAC profile from TAC or IMEI."""
    if re.fullmatch(r"\d{15}", identifier):
        tac = identifier[:8]
    elif re.fullmatch(r"\d{8}", identifier):
        tac = identifier
    else:
        raise ValueError("Invalid input. Must be 8-digit TAC or 15-digit IMEI.")

    profile = TAC_DB.get(tac, {
        "tac": tac,
        "manufacturer": "Unknown",
        "model": "Unknown",
        "device_type": "Unknown",
        "region": "Unknown"
    })

    if profile["manufacturer"] == "Unknown":
        gh_data = fetch_tac_from_github(tac)
        if gh_data:
            profile.update(gh_data)
            TAC_DB[tac] = profile
            save_tac_db(TAC_DB)

    return profile

# -----------------------------
# Cache Management
# -----------------------------
def clear_tac_cache() -> None:
    global TAC_DB
    TAC_DB = {}
    save_tac_db(TAC_DB)

def list_cached_tacs() -> Dict[str, dict]:
    return dict(TAC_DB)

def update_local_cache_from_github() -> None:
    """Download full TAC DB from GitHub and merge into local cache."""
    try:
        r = requests.get(GITHUB_TAC_ZIP, timeout=HTTP_TIMEOUT)
        if r.status_code != 200:
            print("Failed to download TAC DB ZIP.")
            return
        tmp_zip = tempfile.NamedTemporaryFile(delete=False)
        tmp_zip.write(r.content)
        tmp_zip.close()

        with zipfile.ZipFile(tmp_zip.name, 'r') as zip_ref:
            extract_dir = tempfile.mkdtemp()
            zip_ref.extractall(extract_dir)

        tac_folder = None
        for root, dirs, files in os.walk(extract_dir):
            if os.path.basename(root) == "tac":
                tac_folder = root
                break

        if not tac_folder:
            print("TAC folder not found in ZIP.")
            return

        count = 0
        for file in os.listdir(tac_folder):
            if file.endswith(".json"):
                tac_code = file.replace(".json", "")
                with open(os.path.join(tac_folder, file), "r", encoding="utf-8") as f:
                    TAC_DB[tac_code] = json.load(f)
                    count += 1

        save_tac_db(TAC_DB)
        print(f"Updated local TAC cache with {count} entries from GitHub.")
    except requests.RequestException:
        print("Network error while updating cache.")

# -----------------------------
# CLI Test
# -----------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--update-cache":
        update_local_cache_from_github()
    elif len(sys.argv) > 1:
        print(json.dumps(basic_tac_profile(sys.argv[1]), indent=2))
    else:
        print("Usage: python tac_lookup.py <IMEI|TAC> or --update-cache")
