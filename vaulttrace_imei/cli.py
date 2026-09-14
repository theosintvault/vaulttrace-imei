import json
import argparse
from typing import Dict, Any, List

from .carrier_ranges import infer_carrier
from .tac_db import TAC_DB

# ---------------------------
# IMEI Validation
# ---------------------------
def luhn_checksum(imei: str) -> int:
    digits = [int(d) for d in imei]
    for i in range(len(digits) - 2, -1, -2):
        doubled = digits[i] * 2
        digits[i] = doubled - 9 if doubled > 9 else doubled
    return sum(digits) % 10


def validate_imei(imei: str) -> bool:
    return len(imei) == 15 and imei.isdigit() and luhn_checksum(imei) == 0


# ---------------------------
# TAC Profiling (Local DB + Fallback)
# ---------------------------
def basic_tac_profile(tac: str) -> Dict[str, Any]:
    """
    TAC profiler backed by a local TAC_DB.
    No network calls, no disk I/O.
    Always returns a complete dict.
    """

    if tac in TAC_DB:
        entry = TAC_DB[tac]
        return {
            "tac": tac,
            "manufacturer": entry.get("manufacturer", "Unknown"),
            "model": entry.get("model", "Unknown"),
            "region": entry.get("region", "Unknown"),
            "confidence": entry.get("confidence", 0.0),
            "notes": entry.get("notes", []),
            "device_type": entry.get("device_type", "Unknown"),
            "release_year": entry.get("release_year", "Unknown"),
        }

    # Fallback for unknown TACs
    notes = ["No TAC match found in local database."]
    if tac.startswith("35"):
        notes.append("TAC starts with '35' (common smartphone allocation).")
    if tac.startswith("01"):
        notes.append("TAC starts with '01' (older allocation pattern).")

    return {
        "tac": tac,
        "manufacturer": "Unknown",
        "model": "Unknown",
        "region": "Unknown",
        "confidence": 0.0,
        "notes": notes,
        "device_type": "Unknown",
        "release_year": "Unknown",
    }


# ---------------------------
# Anomaly Detection
# ---------------------------
def detect_anomalies(imei: str, profile: Dict[str, Any]) -> List[Dict[str, str]]:
    anomalies: List[Dict[str, str]] = []

    # Repeated digit IMEI (e.g., 111111111111111)
    if imei == imei[0] * 15:
        anomalies.append({
            "msg": "IMEI is composed of a single repeated digit.",
            "severity": "high",
        })

    # TAC starting with 00 often indicates test/unallocated ranges
    if profile["tac"].startswith("00"):
        anomalies.append({
            "msg": "TAC starts with '00' (test or unallocated range).",
            "severity": "high",
        })

    # Low confidence TAC match
    if profile.get("confidence", 0.0) < 0.5:
        anomalies.append({
            "msg": "Low confidence TAC match.",
            "severity": "medium",
        })

    # Carrier vs region mismatch (best-effort heuristic)
    carrier = profile.get("likely_original_carrier")
    region = profile.get("region")
    if carrier and region and carrier != "Unknown" and region != "Unknown":
        if carrier.lower() not in region.lower():
            anomalies.append({
                "msg": f"Carrier '{carrier}' does not appear to match region '{region}'.",
                "severity": "low",
            })

    return anomalies


# ---------------------------
# IMEI Decoder
# ---------------------------
def decode_imei(imei: str) -> Dict[str, Any]:
    if not validate_imei(imei):
        return {
            "imei": imei,
            "valid": False,
            "error": "Invalid IMEI (Luhn or length failed).",
        }

    tac = imei[:8]
    profile = basic_tac_profile(tac)

    result: Dict[str, Any] = {
        "imei": imei,
        "valid": True,
        "tac": tac,
        "manufacturer": profile["manufacturer"],
        "model": profile["model"],
        "region": profile["region"],
        "confidence": profile["confidence"],
        "likely_original_carrier": infer_carrier(tac, profile["region"]),
        "notes": profile["notes"],
        "device_type": profile["device_type"],
        "release_year": profile["release_year"],
    }

    result["anomalies"] = detect_anomalies(imei, result)
    return result


# ---------------------------
# CLI Entry Point
# ---------------------------
def main():
    parser = argparse.ArgumentParser(
        description="VaultTrace IMEI/TAC Decoder (Local TAC DB)"
    )
    parser.add_argument(
        "identifiers",
        nargs="+",
        help="IMEI(s) to decode (15-digit) or TAC(s) (8-digit, best-effort).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format.",
    )
    args = parser.parse_args()

    results:


