# VaultTrace IMEI

VaultTrace IMEI is a precision utility for extracting and correlating TAC data from IMEI identifiers.  
It is intended for analysts conducting telecom OSINT, device attribution, and fraud investigations.  
The tool operates locally and supports offline use with a cached TAC dataset.

---

## Capabilities
- IMEI parsing and checksum validation
- TAC extraction and dataset correlation
- Manufacturer, model, type, and release year identification
- Optional carrier inference when available
- Structured JSON output for automated ingestion
- Offline mode with local TAC database

---

## Deployment
```bash
git clone https://github.com/theosintvault/vaulttrace-imei.git
cd vaulttrace-imei
python3 -m venv venv
source venv/bin/activate
pip install .
