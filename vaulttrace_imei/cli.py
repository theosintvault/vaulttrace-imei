import json
import argparse
from typing import Dict, Any, List
from .carrier_ranges import infer_carrier

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
# PURE LOCAL TAC PROFILER (NO JSON, NO FILES, NO LOOKUPS)
# ---------------------------
def basic_tac_profile(tac: str) -> Dict[str, Any]:
    """
    Fully local TAC profiler.
    No JSON.
    No disk writes.
    No disk reads.
    No online lookups.
    No cache.
    No None returns.
    Always returns a complete dict.
    """

    notes = []

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
def detect_anomalies(imei: str, profile: Dict[str, Any]) -> List[str]:
    anomalies = []

    if imei == imei[0] * 15:
        anomalies.append("IMEI is composed of a single repeated digit.")

    if profile["tac"].startswith("00"):
        anomalies.append("TAC starts with '00' (unallocated or test range).")

    if profile.get("confidence", 0) < 0.5:
        anomalies.append("Low confidence TAC match.")

    carrier = profile.get("likely_original_carrier")
    region = profile.get("region")
    if carrier and region and carrier.lower() not in region.lower():
        anomalies.append(f"Carrier '{carrier}' does not match region '{region}'.")

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
    parser = argparse.ArgumentParser(description="IMEI/TAC Decoder (Pure Local Mode)")
    parser.add_argument("identifiers", nargs="+", help="IMEI(s) or TAC(s) to decode")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    results = [decode_imei(identifier) for identifier in args.identifiers]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for res in results:
            print(f"IMEI: {res['imei']}")
            print(f"  Valid

