"""
Data models for SlothDesk.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class SlothSummary(BaseModel):
    one_liner: str = Field(description="Humorous ultra-short summary so the user doesn't have to read it")
    key_points: List[str] = Field(default_factory=list, description="Top 2-3 key takeaways")
    action_required: bool = Field(default=False, description="Whether the user actually has to get off the couch")
    action_note: Optional[str] = Field(default=None, description="What the lazy human must do, if anything")
    suggested_filename: str = Field(description="Standardized descriptive filename")
    category: str = Field(description="Detected folder category (finance, work, personal, code, reading, media, archives)")
    confidence: float = Field(default=0.9, description="Confidence score 0.0 - 1.0")
    tags: List[str] = Field(default_factory=list, description="Keywords / tags")

class FileRecord(BaseModel):
    id: int
    original_name: str
    current_name: str
    original_path: str
    current_path: str
    category: str
    confidence: float
    summary: str
    tags: List[str] = Field(default_factory=list)
    action_required: bool = False
    action_note: Optional[str] = None
    file_size_bytes: int
    extension: str
    processed_at: str
    undone: bool = False

class QueryResult(BaseModel):
    query: str
    answer: str
    matched_files: List[Dict[str, Any]] = Field(default_factory=list)
    sloth_verdict: str

class SlothStats(BaseModel):
    total_files_processed: int
    minutes_saved: float
    naps_earned: float
    calories_saved: float
    dollars_saved_vs_cloud: float
    categories_breakdown: Dict[str, int]
    sloth_level: str
    recent_activities: List[Dict[str, Any]] = Field(default_factory=list)
