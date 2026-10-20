#!/usr/bin/env python3
"""
1-Click SlothDesk Demo Runner
Demonstrates the entire autonomous workflow:
1. Generates messy clutter
2. Analyzes, classifies, renames, and moves files using Open-Source AI
3. Prints the Sloth Energy Meter stats
4. Performs a local RAG query ("How much was AWS?")
5. Exercises 1-click undo
"""

import sys
import io
import os
from pathlib import Path

# Force UTF-8 encoding on Windows to support emojis cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from sloth_core.config import INCOMING_DIR, BASE_DIR
from sloth_core.organizer import SlothOrganizer
from sloth_core.stats import SlothStatsManager
from sloth_core.rag import SlothRAG
import shutil
from rich.console import Console

console = Console(force_terminal=True, legacy_windows=False)

def run():
    console.print("[bold green]===========================================================[/bold green]")
    console.print("[bold yellow]       🦥 SlothDesk: Autonomous Open-Source AI Demo        [/bold yellow]")
    console.print("[bold green]===========================================================[/bold green]\n")

    organizer = SlothOrganizer()
    stats_mgr = SlothStatsManager(organizer)
    rag = SlothRAG(organizer)

    # Step 1: Copy sample clutter into incoming
    console.print("[bold cyan]Step 1: Dropping messy chaotic files into Incoming Den...[/bold cyan]")
    sample_dir = BASE_DIR / "sample_clutter"
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    for f in sample_dir.iterdir():
        if f.is_file():
            shutil.copy2(f, INCOMING_DIR / f.name)
            console.print(f"  • Landed: [dim]{f.name}[/dim]")

    # Step 2: Autonomous Tidy
    console.print("\n[bold cyan]Step 2: SlothDesk waking up to organize files autonomously...[/bold cyan]")
    results = organizer.tidy_directory(INCOMING_DIR)
    for r in results:
        console.print(f"  ✔ [bold green][{r['category'].upper()}][/bold green] {r['original_name']} -> [white]{r['current_name']}[/white]")
        console.print(f"    [italic]Sloth TL;DR:[/italic] {r['summary']}")

    # Step 3: Stats & Sloth Energy Meter
    console.print("\n[bold cyan]Step 3: Calculating Sloth Energy Meter...[/bold cyan]")
    s = stats_mgr.get_stats()
    console.print(f"  • Files Processed: [bold green]{s.total_files_processed}[/bold green]")
    console.print(f"  • Minutes of Human Effort Spared: [bold green]{s.minutes_saved} mins[/bold green]")
    console.print(f"  • Naps Earned: [bold yellow]{s.naps_earned} 😴[/bold yellow]")
    console.print(f"  • Cloud Dollars Kept in Wallet: [bold green]${s.dollars_saved_vs_cloud:.2f}[/bold green]")
    console.print(f"  • Sloth Level: [bold magenta]{s.sloth_level}[/bold magenta]")

    # Step 4: Ask My Clutter (Local RAG)
    console.print("\n[bold cyan]Step 4: Testing 'Ask My Clutter' Local RAG...[/bold cyan]")
    query = "How much did AWS invoice me for cloud services?"
    console.print(f"  User Query: '[yellow]{query}[/yellow]'")
    ans = rag.ask(query)
    console.print(f"  Answer: [white]{ans['answer']}[/white]")
    console.print(f"  Verdict: [dim italic]{ans['sloth_verdict']}[/dim italic]")

    # Step 5: Test Undo
    console.print("\n[bold cyan]Step 5: Testing 1-Click Safety Undo...[/bold cyan]")
    undo_res = organizer.undo_action()
    console.print(f"  ✔ Restored [yellow]{undo_res.get('restored_name')}[/yellow] to [dim]{undo_res.get('restored_path')}[/dim]")

    console.print("\n[bold green]✔ All demo steps completed with 100% success![/bold green]\n")

if __name__ == "__main__":
    run()
