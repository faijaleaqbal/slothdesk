"""
SlothDesk File Organizer & Database Manager.
Manages automatic sorting, renaming, safe moving, indexing, and 1-click Undo.
"""

import os
import shutil
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from sloth_core.config import (
    ORGANIZED_DIR, DB_PATH, INCOMING_DIR,
    MINUTES_SAVED_PER_FILE_SORT, MINUTES_SAVED_PER_DOCUMENT_READ
)
from sloth_core.extractor import extract_content
from sloth_core.engine import SlothAIEngine
from sloth_core.models import SlothSummary, FileRecord

class SlothOrganizer:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.ai_engine = SlothAIEngine()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes SQLite schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_name TEXT NOT NULL,
                current_name TEXT NOT NULL,
                original_path TEXT NOT NULL,
                current_path TEXT NOT NULL,
                category TEXT NOT NULL,
                confidence REAL NOT NULL,
                summary TEXT NOT NULL,
                tags TEXT NOT NULL,
                action_required INTEGER DEFAULT 0,
                action_note TEXT,
                content_excerpt TEXT,
                file_size_bytes INTEGER NOT NULL,
                extension TEXT NOT NULL,
                processed_at TEXT NOT NULL,
                undone INTEGER DEFAULT 0
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                minutes_saved REAL DEFAULT 0.0
            )
            """)
            conn.commit()

    def organize_file(self, file_path: Path, copy_mode: bool = False) -> Dict[str, Any]:
        """
        Organizes a single file:
        1. Extracts text
        2. Generates open-weight AI analysis & Sloth summary
        3. Moves/copies file into structured category folder with descriptive name
        4. Logs to SQLite
        """
        if not file_path.exists() or file_path.is_dir():
            return {"success": False, "error": f"Invalid file path: {file_path}"}

        original_path = str(file_path.resolve())
        original_name = file_path.name

        # 1. Extract content
        content, meta = extract_content(file_path)

        # 2. Analyze with Open AI Engine
        summary: SlothSummary = self.ai_engine.analyze_file(original_name, content, meta)

        # 3. Determine target directory and filename
        cat_dir = ORGANIZED_DIR / summary.category
        cat_dir.mkdir(parents=True, exist_ok=True)

        target_name = summary.suggested_filename
        target_path = cat_dir / target_name

        # Collision avoidance
        counter = 1
        stem = target_path.stem
        suffix = target_path.suffix
        while target_path.exists():
            target_path = cat_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        # 4. Perform move (or copy if testing)
        try:
            if copy_mode:
                shutil.copy2(file_path, target_path)
            else:
                shutil.move(file_path, target_path)
        except Exception as e:
            return {"success": False, "error": f"Failed to move file: {e}"}

        # 5. Save to database
        now_str = datetime.now().isoformat()
        minutes_saved = MINUTES_SAVED_PER_FILE_SORT + MINUTES_SAVED_PER_DOCUMENT_READ

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO files (
                original_name, current_name, original_path, current_path,
                category, confidence, summary, tags, action_required, action_note,
                content_excerpt, file_size_bytes, extension, processed_at, undone
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                original_name,
                target_path.name,
                original_path,
                str(target_path.resolve()),
                summary.category,
                summary.confidence,
                summary.one_liner,
                json.dumps(summary.tags),
                1 if summary.action_required else 0,
                summary.action_note,
                content[:2000],
                meta.get("size_bytes", 0),
                meta.get("extension", ""),
                now_str
            ))
            file_id = cursor.lastrowid

            cursor.execute("""
            INSERT INTO activity_log (timestamp, event_type, description, minutes_saved)
            VALUES (?, ?, ?, ?)
            """, (
                now_str,
                "file_organized",
                f"Sloth digested '{original_name}' -> '{target_path.name}' in [{summary.category}]",
                minutes_saved
            ))
            conn.commit()

        return {
            "success": True,
            "file_id": file_id,
            "original_name": original_name,
            "current_name": target_path.name,
            "target_path": str(target_path),
            "category": summary.category,
            "summary": summary.one_liner,
            "key_points": summary.key_points,
            "action_required": summary.action_required,
            "action_note": summary.action_note,
            "minutes_saved": minutes_saved
        }

    def tidy_directory(self, source_dir: Path, copy_mode: bool = False) -> List[Dict[str, Any]]:
        """Scans a directory and organizes all loose files."""
        results = []
        if not source_dir.exists():
            return results

        files_to_process = [p for p in source_dir.iterdir() if p.is_file() and not p.name.startswith(".")]
        for f in files_to_process:
            res = self.organize_file(f, copy_mode=copy_mode)
            if res.get("success"):
                results.append(res)
        return results

    def undo_action(self, file_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Reverses the organization of a file or the most recent one.
        Restores it to its original path and marks undone in DB.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if file_id:
                cursor.execute("SELECT * FROM files WHERE id = ? AND undone = 0", (file_id,))
            else:
                cursor.execute("SELECT * FROM files WHERE undone = 0 ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()

            if not row:
                return {"success": False, "message": "No active file organization to undo."}

            current_path = Path(row["current_path"])
            original_path = Path(row["original_path"])

            if current_path.exists():
                # Ensure parent dir exists
                original_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(current_path, original_path)

            cursor.execute("UPDATE files SET undone = 1 WHERE id = ?", (row["id"],))
            cursor.execute("""
            INSERT INTO activity_log (timestamp, event_type, description, minutes_saved)
            VALUES (?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                "file_undone",
                f"Undid organization of '{row['current_name']}' -> restored to '{original_path.name}'",
                -10.0
            ))
            conn.commit()

            return {
                "success": True,
                "file_id": row["id"],
                "restored_name": row["original_name"],
                "restored_path": str(original_path)
            }

    def get_all_files(self, category: Optional[str] = None, include_undone: bool = False) -> List[Dict[str, Any]]:
        """Returns all managed files."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM files WHERE 1=1"
            params = []
            if not include_undone:
                query += " AND undone = 0"
            if category:
                query += " AND category = ?"
                params.append(category)
            query += " ORDER BY id DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            output = []
            for r in rows:
                output.append({
                    "id": r["id"],
                    "original_name": r["original_name"],
                    "current_name": r["current_name"],
                    "category": r["category"],
                    "confidence": r["confidence"],
                    "summary": r["summary"],
                    "tags": json.loads(r["tags"]) if r["tags"] else [],
                    "action_required": bool(r["action_required"]),
                    "action_note": r["action_note"],
                    "file_size_bytes": r["file_size_bytes"],
                    "processed_at": r["processed_at"],
                    "current_path": r["current_path"],
                    "undone": bool(r["undone"])
                })
            return output
