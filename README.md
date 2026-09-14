\# VaultTrace IMEI



VaultTrace IMEI is a lightweight, public‑safe IMEI/TAC decoder and lookup tool.  

It uses public datasets to identify device manufacturer, model, type, and region,  

and can perform basic carrier inference when data is available.



No private TAC/device data is shipped with this tool — all lookups are done against public sources,  

with results cached locally for offline use.



\---



\## Features

\- \*\*IMEI \& TAC decoding\*\* — Extracts TAC from IMEI and validates format

\- \*\*Public dataset lookups\*\* — Uses the GitHub TAC database as a primary source

\- \*\*Local caching\*\* — Stores results for instant offline lookups

\- \*\*Optional full database preload\*\* — Download the entire TAC DB for offline mode

\- \*\*JSON output\*\* — Easy integration with other tools and scripts

\- \*\*Cross‑platform\*\* — Works on Windows, macOS, and Linux



\---



\## Installation



\### 1. Clone the repository

```bash

git clone https://github.com/theosintvault/vaulttrace-imei.git

cd vaulttrace-imei



