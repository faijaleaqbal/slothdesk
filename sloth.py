#!/usr/bin/env python3
"""
SlothDesk - Autonomous Zero-Cloud Desktop Butler
Powered by Open-Source AI.

Usage:
    python sloth.py tidy [--dir PATH]     # Tidy files in folder
    python sloth.py watch [--dir PATH]    # Run background watcher daemon
    python sloth.py serve [--port 8000]   # Launch cozy web dashboard
    python sloth.py stats                 # Print Sloth Energy Meter
    python sloth.py ask "QUESTION"        # Ask your clutter in plain English
    python sloth.py undo                  # Reverse last organization
    python sloth.py demo                  # Load demo chaos and tidy it
"""

import sys
import os
import argparse
import webbrowser
import shutil
from pathlib import Path

# Force UTF-8 encoding on Windows to support emojis cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from sloth_core.config import INCOMING_DIR, BASE_DIR
from sloth_core.organizer import SlothOrganizer
from sloth_core.stats import SlothStatsManager
from sloth_core.rag import SlothRAG
from sloth_core.watcher import SlothWatcher

console = Console(force_terminal=True, legacy_windows=False)

def cmd_tidy(source_dir: Path = None):
    organizer = SlothOrganizer()
    src = source_dir or INCOMING_DIR
    console.print(f"\n[bold green]🦥 SlothDesk waking up gently...[/bold green] Scanning: [cyan]{src}[/cyan]")

    results = organizer.tidy_directory(src)
    if not results:
        console.print("[dim]No files found to tidy. Sloth is going back to sleep.[/dim]\n")
        return

    table = Table(title="🦥 Digested Files Summary", header_style="bold green")
    table.add_column("Category", style="cyan")
    table.add_column("Original Name", style="dim")
    table.add_column("Organized As", style="bold white")
    table.add_column("Sloth TL;DR", style="italic green")
    table.add_column("Action Needed?", style="yellow")

    for r in results:
        act_str = f"⚠️ {r['action_note']}" if r.get("action_required") else "None (Chill)"
        table.add_row(
            r["category"].upper(),
            r["original_name"],
            r["current_name"],
            r["summary"][:65] + "...",
            act_str
        )

    console.print(table)
    stats_mgr = SlothStatsManager(organizer)
    stats = stats_mgr.get_stats()
    console.print(f"[bold yellow]😴 Naps Earned Today:[/bold yellow] [bold white]{stats.naps_earned}[/bold white] | [bold green]Effort Saved:[/bold green] {stats.minutes_saved} mins\n")

def cmd_stats():
    organizer = SlothOrganizer()
    stats_mgr = SlothStatsManager(organizer)
    s = stats_mgr.get_stats()

    content = f"""
[bold yellow]Sloth Rank:[/bold yellow] {s.sloth_level}

[bold]• Total Files Digested:[/bold] {s.total_files_processed}
[bold]• Human Suffering Saved:[/bold] {s.minutes_saved} minutes
[bold]• Naps Earned:[/bold] {s.naps_earned} naps (15m units)
[bold]• Brain Calories Conserved:[/bold] {s.calories_saved} kcal
[bold]• Cloud API Dollars Saved:[/bold] ${s.dollars_saved_vs_cloud:.2f} (Zero corporate tokens)

[bold green]Category Breakdown:[/bold green]
"""
    for cat, count in s.categories_breakdown.items():
        content += f"  - [cyan]{cat.capitalize()}:[/cyan] {count} files\n"

    console.print(Panel(content.strip(), title="🦥 The Sloth Energy Meter", border_style="green"))

def cmd_ask(query: str):
    organizer = SlothOrganizer()
    rag = SlothRAG(organizer)
    console.print(f"\n[bold green]🦥 Asking SlothDen:[/bold green] '[dim]{query}[/dim]'")
    res = rag.ask(query)

    console.print(Panel(
        f"{res['answer']}\n\n[dim italic]Verdict: {res.get('sloth_verdict', '')}[/dim italic]",
        title="🦥 Local Open-Weight Response",
        border_style="cyan"
    ))

def cmd_undo():
    organizer = SlothOrganizer()
    res = organizer.undo_action()
    if res.get("success"):
        console.print(f"[bold green]↩️ Undone![/bold green] Restored [cyan]{res['restored_name']}[/cyan] to [dim]{res['restored_path']}[/dim]")
    else:
        console.print(f"[yellow]{res.get('message', 'Nothing to undo.')}[/yellow]")

def cmd_watch(source_dir: Path = None):
    organizer = SlothOrganizer()
    src = source_dir or INCOMING_DIR
    console.print(f"[bold green]🦥 Sloth Watcher Daemon running in background...[/bold green]")
    console.print(f"Monitoring: [cyan]{src}[/cyan]")
    console.print("Press Ctrl+C to stop and go back to human chores.\n")

    def on_file_organized(res):
        console.print(f"[green]✔ Digested:[/green] [white]{res['original_name']}[/white] -> [bold cyan][{res['category']}][/bold cyan] {res['current_name']}")
        console.print(f"   [italic green]TL;DR:[/italic green] {res['summary']}\n")

    watcher = SlothWatcher(watch_dir=src, organizer=organizer, interval=2.5)
    watcher.start(callback=on_file_organized)
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        console.print("\n[yellow]Sloth daemon stopped.[/yellow]")

def cmd_serve(port: int = 8000):
    import uvicorn
    console.print(f"\n[bold green]🦥 Starting SlothDesk Web Server on http://localhost:{port}[/bold green]")
    webbrowser.open(f"http://localhost:{port}")
    uvicorn.run("web.app:app", host="0.0.0.0", port=port, reload=False)

def cmd_demo():
    console.print("\n[bold yellow]🎲 Generating chaotic demo clutter in ~/SlothDen/Incoming...[/bold yellow]")
    sample_dir = BASE_DIR / "sample_clutter"
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    for f in sample_dir.iterdir():
        if f.is_file():
            shutil.copy2(f, INCOMING_DIR / f.name)
    console.print("[green]✔ Clutter created! Now running autonomous tidy...[/green]")
    cmd_tidy(INCOMING_DIR)

def main():
    parser = argparse.ArgumentParser(description="SlothDesk: Autonomous Zero-Cloud Desktop Butler")
    subparsers = parser.add_subparsers(dest="command")

    # tidy
    p_tidy = subparsers.add_parser("tidy", help="Organize files in directory")
    p_tidy.add_argument("--dir", type=str, default=None, help="Directory to tidy")

    # watch
    p_watch = subparsers.add_parser("watch", help="Start background watcher daemon")
    p_watch.add_argument("--dir", type=str, default=None, help="Directory to monitor")

    # serve
    p_serve = subparsers.add_parser("serve", help="Launch cozy web UI")
    p_serve.add_argument("--port", type=int, default=8000, help="Port number")

    # stats
    subparsers.add_parser("stats", help="Print Sloth Energy Meter")

    # ask
    p_ask = subparsers.add_parser("ask", help="Ask your clutter questions")
    p_ask.add_argument("query", type=str, help="Question to ask")

    # undo
    subparsers.add_parser("undo", help="Undo last file organization")

    # demo
    subparsers.add_parser("demo", help="Run self-contained demo with sample clutter")

    args = parser.parse_args()

    if args.command == "tidy":
        cmd_tidy(Path(args.dir) if args.dir else None)
    elif args.command == "watch":
        cmd_watch(Path(args.dir) if args.dir else None)
    elif args.command == "serve":
        cmd_serve(args.port)
    elif args.command == "stats":
        cmd_stats()
    elif args.command == "ask":
        cmd_ask(args.query)
    elif args.command == "undo":
        cmd_undo()
    elif args.command == "demo":
        cmd_demo()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
