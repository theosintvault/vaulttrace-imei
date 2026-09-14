#!/usr/bin/env python3
"""
basic_tac_profile.py
Multi-source TAC lookup: GitHub TAC DB -> tacapi.com -> imeiapi.com
"""

import re
import sys
import json
import os
import urllib.request

# Data sources
GITHUB_TAC_URL = "https://raw.githubusercontent.com/MoazEb/tac-database/main/tac/"
TACAPI_URL = "https://tacapi.com/api/v1/tac/"
IMEIAPI_URL = "https://api.imeiapi.com/api/v1/tac/"  # Public endpoint for TAC lookup

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


def fetch_from_github(tac):
    data = fetch_json(f"{GITHUB_TAC_URL}{tac}.json")
    if data and isinstance(data, dict) and data.get("brand"):
        return {
            "brand": data.get("brand", "").strip(),
            "model": data.get("model", "").strip(),
            "type": data.get("type", "").strip()
        }
    return None


def fetch_from_tacapi(tac):
    data = fetch_json(f"{TACAPI_URL}{tac}")
    if data and isinstance(data, dict) and data.get("brand"):
        return {
            "brand": str(data.get("brand", "")).strip(),
            "model": str(data.get("model", "")).strip(),
            "type": str(data.get("type", "")).strip()
        }
    return None


def fetch_from_imeiapi(tac):
    data = fetch_json(f"{IMEIAPI_URL}{tac}")
    if data and isinstance(data, dict) and data.get("brand"):
        return {
            "brand": str(data.get("brand", "")).strip(),
            "model": str(data.get("model", "")).strip(),
            "type": str(data.get("type", "")).strip()
        }
    return None


def basic_tac_profile(imei):
    if not re.fullmatch(r"\d{15}", imei):
        return {"error": "Invalid IMEI format. Must be 15 digits."}

    tac = imei[:8]
    cache = load_cache()

    if tac in cache:
        return {"TAC": tac, **cache[tac]}

    # Try sources in order
    for fetcher in (fetch_from_github, fetch_from_tacapi, fetch_from_imeiapi):
        data = fetcher(tac)
        if data:
            cache[tac] = data
            save_cache(cache)
            return {"TAC": tac, **data}

    # No data found
    cache[tac] = {"brand": "", "model": "", "type": ""}
    save_cache(cache)
    return {"TAC": tac, "brand": "", "model": "", "type": ""}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python basic_tac_profile.py <IMEI>")
        sys.exit(1)

    imei_input = sys.argv[1]
    result = basic_tac_profile(imei_input)

    for key, value in result.items():
        print(f"{key}: {value}")


