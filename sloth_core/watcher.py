"""
SlothDesk Background Watcher Daemon.
Sleepily monitors an incoming directory (e.g. Downloads or ~/SlothDen/Incoming)
and autonomously digests any newly dropped files.
"""

import time
import threading
from pathlib import Path
from typing import Callable, Optional
from sloth_core.organizer import SlothOrganizer
from sloth_core.config import INCOMING_DIR

class SlothWatcher:
    def __init__(self, watch_dir: Path = INCOMING_DIR, organizer: Optional[SlothOrganizer] = None, interval: float = 4.0):
        self.watch_dir = watch_dir
        self.organizer = organizer or SlothOrganizer()
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable[[dict], None]] = None

    def start(self, callback: Optional[Callable[[dict], None]] = None):
        """Starts background watcher thread."""
        if self._running:
            return
        self.callback = callback
        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stops the watcher."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _watch_loop(self):
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        while self._running:
            try:
                for item in self.watch_dir.iterdir():
                    if item.is_file() and not item.name.startswith(".") and not item.name.endswith(".tmp"):
                        # Ensure file is done writing
                        initial_size = item.stat().st_size
                        time.sleep(0.5)
                        if item.exists() and item.stat().st_size == initial_size:
                            res = self.organizer.organize_file(item)
                            if self.callback and res.get("success"):
                                self.callback(res)
            except Exception:
                pass
            time.sleep(self.interval)
