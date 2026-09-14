# VaultTrace IMEI

> Device Intelligence. Simplified.

VaultTrace IMEI is a precision tool for decoding and profiling IMEI/TAC identifiers.  
Designed for OSINT practitioners, telecom analysts, and security researchers, it leverages public TAC datasets to identify device manufacturer, model, type, and region — with optional carrier inference when available.

No proprietary or private TAC data is included. All lookups are performed against public sources, with results cached locally for offline use.

---

## Capabilities
- **IMEI/TAC Decoding** — Extracts TAC from IMEI and validates format integrity
- **Public Dataset Correlation** — Matches TAC against open-source TAC databases
- **Offline Intelligence Mode** — Local caching for air‑gapped environments
- **Full Database Preload** — Optional complete TAC DB for rapid lookups
- **Structured Output** — JSON format for integration into intelligence pipelines
- **Cross‑Platform** — Windows, macOS, Linux

---

## Deployment

Clone the repository:
```bash
git clone https://github.com/theosintvault/vaulttrace-imei.git
cd vaulttrace-imei
