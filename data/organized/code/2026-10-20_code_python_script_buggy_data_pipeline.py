"""
Data Pipeline ETL Script
Extracts messy logs and writes normalized JSON.
"""

import sys
import json
from pathlib import Path

def parse_access_log(log_path: str):
    records = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if "ERROR" in line or "WARN" in line:
                parts = line.strip().split(" - ")
                records.append({
                    "timestamp": parts[0] if len(parts) > 0 else "unknown",
                    "level": "WARN" if "WARN" in line else "ERROR",
                    "message": parts[-1]
                })
    return records

if __name__ == "__main__":
    print(f"Processed records: {len(parse_access_log('server.log'))}")
