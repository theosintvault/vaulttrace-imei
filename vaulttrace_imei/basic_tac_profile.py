#!/usr/bin/env python3
"""
basic_tac_profile.py
Look up TAC (Type Allocation Code) information from an IMEI.
Checks local cache, then GitHub TAC database, then a free fallback API.
"""

import re
import sys
import json
import os
import urllib.request

# URLs
GITHUB_TAC_URL = "https://raw.githubusercontent.com/MoazEb/tac-database/main/tac/"
FALLBACK_API_URL = "https://tacapi.com/api/v1/tac/"

# Local cache file (same folder as script)
CACHE_FILE = os.path.join(os.path.dirname(__file__), "tac_db.json")


def load_cache():
    """Load local TAC cache from JSON file."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            print("Warning: Cache file invalid or unreadable. Starting fresh.")
            return {}
    return {}


def save_cache(cache):
    """Save TAC cache to JSON file."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except OSError as e:
        print(f"Warning: Could not save cache: {e}")


def fetch_from_github(tac):
    """Fetch TAC info from GitHub TAC database."""
    url = f"{GITHUB_TAC_URL}{tac}.json"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                # Ensure only real data is returned
                if isinstance(data, dict) and data:
                    return {
                        "brand": data.get("brand", "").strip(),
                        "model": data.get("model", "").strip(),
                        "type": data.get("type", "").strip()
                    }
    except Exception:
        pass
    return None


def fetch_from_fallback_api(tac):
    """Fetch TAC info from fallback API."""
    url = f"{FALLBACK_API_URL}{tac}"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                if isinstance(data, dict) and data:
                    return {
                        "brand": str(data.get("brand", "")).strip(),
                        "model": str(data.get("model", "")).strip(),
                        "type": str(data.get("type", "")).strip()
                    }
    except Exception:
        pass
    return None


def basic_tac_profile(imei):
    """Return TAC profile for a given IMEI."""
    if not re.fullmatch(r"\d{15}", imei):
        return {"error": "Invalid IMEI format. Must be 15 digits."}

    tac = imei[:8]
    cache = load_cache()

    # Check local cache first
    if tac in cache:
        return {"TAC": tac, **cache[tac]}

    # Try GitHub TAC database
    data = fetch_from_github(tac)
    if data:
        cache[tac] = data
        save_cache(cache)
        return {"TAC": tac, **data}

    # Try fallback API
    data = fetch_from_fallback_api(tac)
    if data:
        cache[tac] = data
        save_cache(cache)
        return {"TAC": tac, **data}

    # No data found anywhere
    return {"TAC": tac, "brand": "", "model": "", "type": ""}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python basic_tac_profile.py <IMEI>")
        sys.exit(1)

    imei_input = sys.argv[1]
    result = basic_tac_profile(imei_input)

    for key, value in result.items():
        print(f"{key}: {value}")



