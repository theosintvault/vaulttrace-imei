#!/usr/bin/env python3
"""
basic_tac_profile.py
Multi-source TAC lookup with flexible key mapping for different datasets.
"""

import re
import sys
import json
import os
import urllib.request

# Data sources
GITHUB_TAC_URL = "https://raw.githubusercontent.com/MoazEb/tac-database/main/tac/"
TACAPI_URL = "https://tacapi.com/api/v1/tac/"

# Local cache file
CACHE_FILE = os.path.join(os.path.dirname(__file__), "tac_db.json")


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass


def fetch_json(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status == 200:
                return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None
    return None


def normalize_tac_data(data):
    """Map various possible TAC dataset keys to standard output keys."""
    if not isinstance(data, dict):
        return None
    return {
        "brand": data.get("brand") or data.get("brand_name") or data.get("manufacturer") or "",
        "model": data.get("model") or data.get("model_name") or data.get("device") or data.get("marketing_name") or "",
        "type": data.get("type") or data.get("equipment_type") or ""
    }


def fetch_from_github(tac):
    data = fetch_json(f"{GITHUB_TAC_URL}{tac}.json")
    return normalize_tac_data(data)


def fetch_from_tacapi(tac):
    data = fetch_json(f"{TACAPI_URL}{tac}")
    return normalize_tac_data(data)


def basic_tac_profile(imei):
    if not re.fullmatch(r"\d{15}", imei):
        return {"error": "Invalid IMEI format. Must be 15 digits."}

    tac = imei[:8]
    cache = load_cache()

    if tac in cache:
        return {"TAC": tac, **cache[tac]}

    # Try sources in order
    for fetcher in (fetch_from_github, fetch_from_tacapi):
        data = fetcher(tac)
        if data and (data["brand"] or data["model"] or data["type"]):
            cache[tac] = data
            save_cache(cache)
            return {"TAC": tac, **data}

    # No data found
    unknown_data = {
        "brand": "",
        "brand_name": "",
        "manufacturer": "",
        "model": "",
        "model_name": "",
        "device": "",
        "marketing_name": "",
        "equipment_type": "",
        "type": ""
    }
    cache[tac] = unknown_data
    save_cache(cache)
    return {"TAC": tac, **unknown_data}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python basic_tac_profile.py <IMEI>")
        sys.exit(1)

    imei_input = sys.argv[1]
    result = basic_tac_profile(imei_input)

    print(f"TAC: {result['TAC']}")
    print(f"Brand: {result.get('brand') or result.get('brand_name') or result.get('manufacturer')}")
    print(f"Model: {result.get('model') or result.get('model_name') or result.get('device') or result.get('marketing_name')}")
    print(f"Type: {result.get('type') or result.get('equipment_type')}")



