"""
SlothDesk Statistics & Energy Meter.
Tracks human effort conserved, naps earned, and cloud dollars saved.
"""

from typing import Dict, Any
from sloth_core.organizer import SlothOrganizer
from sloth_core.models import SlothStats
from sloth_core.config import (
    CALORIES_SAVED_PER_MIN, COST_SAVED_PER_CLOUD_CALL_USD, SLOTH_NAP_UNIT_MINUTES
)

class SlothStatsManager:
    def __init__(self, organizer: SlothOrganizer):
        self.organizer = organizer

    def get_stats(self) -> SlothStats:
        with self.organizer._get_connection() as conn:
            cursor = conn.cursor()

            # Files count
            cursor.execute("SELECT COUNT(*) FROM files WHERE undone = 0")
            total_files = cursor.fetchone()[0]

            # Minutes saved
            cursor.execute("SELECT SUM(minutes_saved) FROM activity_log")
            row = cursor.fetchone()
            minutes_saved = row[0] if (row and row[0] is not None) else 0.0

            # Categories breakdown
            cursor.execute("""
            SELECT category, COUNT(*) as cnt
            FROM files
            WHERE undone = 0
            GROUP BY category
            """)
            categories = {r["category"]: r["cnt"] for r in cursor.fetchall()}

            # Recent activities
            cursor.execute("""
            SELECT timestamp, event_type, description, minutes_saved
            FROM activity_log
            ORDER BY id DESC LIMIT 8
            """)
            activities = [dict(r) for r in cursor.fetchall()]

        naps_earned = round(minutes_saved / SLOTH_NAP_UNIT_MINUTES, 1)
        calories_saved = round(minutes_saved * CALORIES_SAVED_PER_MIN, 1)
        dollars_saved = round(total_files * COST_SAVED_PER_CLOUD_CALL_USD, 2)

        # Sloth Ranking
        if total_files == 0:
            level = "Hyperactive Human (Needs Nap)"
        elif total_files < 5:
            level = "Drowsy Koala"
        elif total_files < 15:
            level = "Three-Toed Apprentice"
        elif total_files < 30:
            level = "Zen Tree-Hugger"
        else:
            level = "Grandmaster Sloth 🦥 (Supreme Conservation of Energy)"

        return SlothStats(
            total_files_processed=total_files,
            minutes_saved=round(minutes_saved, 1),
            naps_earned=naps_earned,
            calories_saved=calories_saved,
            dollars_saved_vs_cloud=dollars_saved,
            categories_breakdown=categories,
            sloth_level=level,
            recent_activities=activities
        )
