import json
import argparse
from typing import Dict, Any, List
from .carrier_ranges import infer_carrier
from .tac_lookup import basic_tac_profile  # <-- Use your extended TAC lookup here

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
# Anomaly Detection
# ---------------------------
def detect_anomalies(imei: str, profile: Dict[str, Any]) -> List[str]:
    anomalies = []

    # Check for all zeros or repeated digits
    if imei == imei[0] * 15:
        anomalies.append("IMEI is composed of a single repeated digit.")

    # Check for TAC patterns that are unusual
    if profile["tac"].startswith("00"):
        anomalies.append("TAC starts with '00' (unallocated or test range).")

    # Check for low confidence TAC
    if profile.get("confidence", 0) < 0.5:
        anomalies.append("Low confidence TAC match.")

    # Check for carrier-region mismatch
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
    profile = basic_tac_profile(tac)  # Pulls from local + online TAC DB

    result: Dict[str, Any] = {
        "imei": imei,
        "valid": True,
        "tac": tac,
        "manufacturer": profile.get("manufacturer", "Unknown"),
        "model": profile.get("model", "Unknown"),
        "region": profile.get("region", "Unknown"),
        "confidence": profile.get("confidence", 0.0),
        "likely_original_carrier": infer_carrier(tac, profile.get("region", "Unknown")),
        "notes": profile.get("notes", []),
        "device_type": profile.get("device_type", "Unknown"),
        "release_year": profile.get("release_year", "Unknown"),
    }

    # Add anomaly flags
    result["anomalies"] = detect_anomalies(imei, result)

    return result

# ---------------------------
# CLI Entry Point
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="IMEI/TAC Decoder with Anomaly Detection")
    parser.add_argument("identifiers", nargs="+", help="IMEI(s) or TAC(s) to decode")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    results = [decode_imei(identifier) for identifier in args.identifiers]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for res in results:
            print(f"IMEI: {res['imei']}")
            print(f"  Valid: {res['valid']}")
            if res["valid"]:
                print(f"  TAC: {res['tac']}")
                print(f"  Manufacturer: {res['manufacturer']}")
                print(f"  Model: {res['model']}")
                print(f"  Region: {res['region']}")
                print(f"  Device Type: {res['device_type']}")
                print(f"  Release Year: {res['release_year']}")
                print(f"  Confidence: {res['confidence']}")
                print(f"  Likely Original Carrier: {res['likely_original_carrier']}")
                print(f"  Notes: {', '.join(res['notes']) if res['notes'] else 'None'}")
                print(f"  Anomalies: {', '.join(res['anomalies']) if res['anomalies'] else 'None'}")
            else:
                print(f"  Error: {res['error']}")
            print("-" * 40)

if __name__ == "__main__":
    main()

