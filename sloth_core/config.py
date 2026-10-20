"""
SlothDesk Configuration
Central settings, directory paths, and sloth metrics constants.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Watch & Organization directories
INCOMING_DIR = Path(os.getenv("SLOTH_INCOMING_DIR", DATA_DIR / "incoming"))
ORGANIZED_DIR = Path(os.getenv("SLOTH_ORGANIZED_DIR", DATA_DIR / "organized"))
ARCHIVE_DIR = Path(os.getenv("SLOTH_ARCHIVE_DIR", DATA_DIR / "archive"))
DB_PATH = Path(os.getenv("SLOTH_DB_PATH", DATA_DIR / "slothdesk.db"))

for p in (INCOMING_DIR, ORGANIZED_DIR, ARCHIVE_DIR):
    p.mkdir(parents=True, exist_ok=True)

# AI Engine Settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("SLOTH_MODEL", "llama3.2:1b")
PREFER_LOCAL_OLLAMA = os.getenv("PREFER_LOCAL_OLLAMA", "true").lower() in ("true", "1", "yes")

# Sloth Energy & Laziness Constants
# Based on productivity studies of decision fatigue and manual digital hoard management:
MINUTES_SAVED_PER_FILE_SORT = 3.5      # Finding folder, dragging, deciding where to put it
MINUTES_SAVED_PER_DOCUMENT_READ = 7.0   # Skimming & understanding contents
CALORIES_SAVED_PER_MIN = 1.4            # Brain glucose expenditure saved
COST_SAVED_PER_CLOUD_CALL_USD = 0.035   # Average cloud LLM API cost saved (GPT-4o / Claude Sonnet)
SLOTH_NAP_UNIT_MINUTES = 15.0           # 15 mins of saved effort = 1 well-deserved sloth nap!

# Category Definitions
CATEGORIES = {
    "finance": "Invoices, receipts, tax forms, bank statements, bills, expenses",
    "work": "Meeting notes, project plans, briefs, sprint summaries, slide decks",
    "personal": "Medical lab results, travel tickets, warranties, letters, journal",
    "code": "Scripts, source code, config files, git patches, log outputs",
    "reading": "Articles, research papers, book chapters, essays, reading lists",
    "media": "Images, audio files, screenshots, video clips, assets",
    "archives": "Zip bundles, old dumps, backups, misc historical items",
}
