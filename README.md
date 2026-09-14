VaultTrace IMEI
VaultTrace IMEI is a focused utility for analyzing IMEI identifiers and correlating TAC values with device intelligence. The tool is built for OSINT practitioners, forensic analysts, telecom researchers, and fraud investigators who need reliable IMEI interpretation without external dependencies. All processing is local and transparent.

Overview
An IMEI contains a TAC block that identifies the device family. VaultTrace IMEI extracts the TAC, validates the IMEI structure, and maps the TAC to manufacturer, model, region, device type, and release year using a local dataset. The tool also performs anomaly checks to highlight irregular or suspicious identifiers.

The project is designed for environments where offline operation, reproducibility, and data integrity matter.

Features
Full IMEI parsing and Luhn checksum validation

TAC extraction and correlation with a local dataset

Manufacturer, model, region, device type, and release year identification

Confidence scoring for TAC matches

Optional carrier inference when available

Structured JSON output for automation and ingestion

Local-only operation with no network calls

Basic anomaly detection with severity levels

CLI interface for single or multiple identifiers
