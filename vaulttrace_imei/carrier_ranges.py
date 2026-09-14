from typing import Optional, List, Dict

# Offline TAC prefix rules for major carriers
# These are example prefixes — replace or extend with verified TAC data
CARRIER_RULES: List[Dict] = [
    {
        "name": "Verizon Wireless",
        "regions": ["US"],
        "notes": "Covers common Verizon-assigned TAC ranges for LTE/5G devices.",
        "tac_prefixes": ["35", "9900", "9901"]  # Example: 35xxxxxx, 9900xxxx
    },
    {
        "name": "AT&T Mobility",
        "regions": ["US"],
        "notes": "Covers AT&T-assigned TAC ranges for smartphones and IoT devices.",
        "tac_prefixes": ["01", "3529", "3530"]
    },
    {
        "name": "T-Mobile USA",
        "regions": ["US"],
        "notes": "Covers T-Mobile-assigned TAC ranges.",
        "tac_prefixes": ["3548", "3550", "3560"]
    },
    {
        "name": "Vodafone Group",
        "regions": ["UK", "EU"],
        "notes": "Covers Vodafone TAC ranges across Europe.",
        "tac_prefixes": ["3520", "3521", "3556"]
    },
    {
        "name": "Telefonica / Movistar",
        "regions": ["ES", "EU", "LATAM"],
        "notes": "Covers Telefonica TAC ranges in Spain and Latin America.",
        "tac_prefixes": ["3534", "3542"]
    },
    {
        "name": "Orange Group",
        "regions": ["FR", "EU", "AF"],
        "notes": "Covers Orange TAC ranges in Europe and Africa.",
        "tac_prefixes": ["3569", "3570"]
    }
]

def infer_carrier(tac: str, region: Optional[str] = None) -> str:
    """
    Offline-only carrier inference based on TAC prefix and optional region.
    Matches longest TAC prefix first for accuracy.
    """
    tac = tac.strip()
    if not tac.isdigit() or len(tac) < 2:
        return "Unknown"

    # Normalize region for case-insensitive matching
    region = region.upper() if region else None

    # Sort rules so longer prefixes match first
    sorted_rules = sorted(
        CARRIER_RULES,
        key=lambda r: max(len(p) for p in r.get("tac_prefixes", [])),
        reverse=True
    )

    for rule in sorted_rules:
        # If region is provided, skip rules that don't match
        if region and region not in [r.upper() for r in rule.get("regions", [])]:
            continue

        for prefix in rule.get("tac_prefixes", []):
            if tac.startswith(prefix):
                return rule["name"]

    return "Unknown"

