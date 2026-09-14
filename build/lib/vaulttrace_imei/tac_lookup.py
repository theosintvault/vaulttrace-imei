"""
tac_lookup.py
-------------
Handles TAC (Type Allocation Code) and IMEI lookups.

Features:
- Offline-first lookup from local tac_db.json
- Online enrichment from public TAC database (GitHub)
- Optional GSMA TAC mirror scraping (if available)
- Automatic caching of new TACs
- Robust input validation and error handling
- Utility functions for cache management
"""

import json
import os
import re
import requests
from typing import Dict, Optional

# -----------------------------
# Configuration
# -----------------------------

# Path to local TAC database
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "tac_db.json")

# Public TAC database (GitHub)
GITHUB_TAC_BASE = "https://raw.githubusercontent.com/MoazEb/tac-database/main/tac"

# HTTP request settings
HTTP_TIMEOUT = 5  # seconds


# -----------------------------
# Local DB Handling
# -----------------------------

def load_tac_db() -> Dict[str, dict]:
    """
    Load TAC database from local JSON file.
    Returns an empty dict if file doesn't exist or is invalid.
    """
    if not os.path.exists(LOCAL_DB_PATH):
        return {}
    try:
        with open(LOCAL_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_tac_db(db: Dict[str, dict]) -> None:
    """
    Save TAC database to local JSON file.
    """
    try:
        with open(LOCAL_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
    except OSError:
        pass


# Load DB into memory
TAC_DB = load_tac_db()


# -----------------------------
# Online Sources
# -----------------------------

def fetch_tac_from_github(tac: str) -> Optional[dict]:
    """
    Fetch TAC details from the public GitHub TAC database.
    Returns None if not found or request fails.
    """
    try:
        url = f"{GITHUB_TAC_BASE}/{tac}.json"
        r = requests.get(url, timeout=HTTP_TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None


def fetch_tac_from_gsma(tac: str) -> Optional[dict]:
    """
    Placeholder for GSMA TAC mirror scraping.
    This can be implemented if you have access to a GSMA TAC source.
    """
    # Example: scraping logic would go here
    return None


# -----------------------------
# Main Lookup Function
# -----------------------------

def basic_tac_profile(identifier: str) -> dict:
    """
    Returns TAC profile from either a TAC code or a full IMEI.
    Falls back to GitHub TAC DB if not found locally.
    """
    # Validate and extract TAC
    if re.fullmatch(r"\d{15}", identifier):
        tac = identifier[:8]
    elif re.fullmatch(r"\d{8}", identifier):
        tac = identifier
    else:
        raise ValueError("Invalid input. Must be 8-digit TAC or 15-digit IMEI.")

    # Lookup in local DB
    profile = TAC_DB.get(tac, {
        "tac": tac,
        "manufacturer": "Unknown",
        "model": "Unknown",
        "device_type": "Unknown",
        "region": "Unknown"
    })

    # If not found locally, try online sources
    if profile["manufacturer"] == "Unknown":
        # Try GitHub
        gh_data = fetch_tac_from_github(tac)
        if gh_data:
            profile.update(gh_data)

        # Try GSMA (optional)
        if profile["manufacturer"] == "Unknown":
            gsma_data = fetch_tac_from_gsma(tac)
            if gsma_data:
                profile.update(gsma_data)

        # Save to local DB if we found something
        if profile["manufacturer"] != "Unknown":
            TAC_DB[tac] = profile
            save_tac_db(TAC_DB)

    return profile


# -----------------------------
# Utility Functions
# -----------------------------

def clear_tac_cache() -> None:
    """Clear the local TAC database."""
    global TAC_DB
    TAC_DB = {}
    save_tac_db(TAC_DB)


def list_cached_tacs() -> Dict[str, dict]:
    """Return all cached TAC entries."""
    return dict(TAC_DB)


def cache_tac_entry(tac: str, manufacturer: str, model: str,
                    device_type: str = "Unknown", region: str = "Unknown") -> None:
    """
    Manually add a TAC entry to the local database.
    """
    TAC_DB[tac] = {
        "tac": tac,
        "manufacturer": manufacturer,
        "model": model,
        "device_type": device_type,
        "region": region
    }
    save_tac_db(TAC_DB)


# -----------------------------
# CLI Test
# -----------------------------

if __name__ == "__main__":
    # Simple test run
    test_imei = "356938035643809"
    print(json.dumps(basic_tac_profile(test_imei), indent=2))
