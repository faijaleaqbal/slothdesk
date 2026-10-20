"""
FastAPI Server for SlothDesk Web Dashboard & API.
"""

import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from sloth_core.config import INCOMING_DIR, ORGANIZED_DIR, BASE_DIR
from sloth_core.organizer import SlothOrganizer
from sloth_core.stats import SlothStatsManager
from sloth_core.rag import SlothRAG
from sloth_core.watcher import SlothWatcher

app = FastAPI(title="SlothDesk", description="Autonomous Zero-Cloud Desktop Butler powered by Open AI")

# Instantiate managers
organizer = SlothOrganizer()
stats_manager = SlothStatsManager(organizer)
rag_engine = SlothRAG(organizer)
watcher = SlothWatcher(watch_dir=INCOMING_DIR, organizer=organizer)

# Models
class AskRequest(BaseModel):
    query: str

class UndoRequest(BaseModel):
    file_id: Optional[int] = None

class TidyRequest(BaseModel):
    source_dir: Optional[str] = None

@app.on_event("startup")
def startup_event():
    # Start background watcher
    watcher.start()

@app.on_event("shutdown")
def shutdown_event():
    watcher.stop()

@app.get("/api/status")
def get_status():
    ai_status = organizer.ai_engine.check_ollama_status()
    return {
        "status": "online",
        "watcher_active": watcher._running,
        "incoming_dir": str(INCOMING_DIR),
        "organized_dir": str(ORGANIZED_DIR),
        "ai": ai_status
    }

@app.get("/api/stats")
def get_stats():
    return stats_manager.get_stats()

@app.get("/api/files")
def get_files(category: Optional[str] = None):
    return organizer.get_all_files(category=category)

@app.post("/api/tidy")
def trigger_tidy(req: TidyRequest):
    src = Path(req.source_dir) if req.source_dir else INCOMING_DIR
    results = organizer.tidy_directory(src)
    return {
        "success": True,
        "processed_count": len(results),
        "items": results
    }

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Receives a dropped file, saves it to incoming, and lets Sloth digest it immediately."""
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = INCOMING_DIR / file.filename
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process immediately
    result = organizer.organize_file(temp_path)
    return result

@app.post("/api/undo")
def undo_action(req: UndoRequest):
    result = organizer.undo_action(req.file_id)
    return result

@app.post("/api/ask")
def ask_clutter(req: AskRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    return rag_engine.ask(req.query)

@app.post("/api/populate-demo")
def populate_demo():
    """Generates a batch of chaotic real-world clutter in the incoming folder for testing."""
    sample_dir = BASE_DIR / "sample_clutter"
    count = 0
    if sample_dir.exists():
        for f in sample_dir.iterdir():
            if f.is_file():
                dest = INCOMING_DIR / f.name
                shutil.copy2(f, dest)
                count += 1
    return {"success": True, "files_created": count, "message": "Chaotic clutter dropped into incoming folder."}

# Mount static files
static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def serve_index():
    index_file = static_dir / "index.html"
    return FileResponse(str(index_file))
