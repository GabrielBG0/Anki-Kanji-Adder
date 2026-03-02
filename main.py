import json
import os
import re
import sys

from rich.console import Console
from rich.prompt import Prompt

from anki import find_notes, get_notes, list_decks, update_note
from jmdict import JMDict
from matcher import rank_candidates
from rollback import generate_session_id, get_sessions, log_change, rollback_session

console = Console()
jmdict = JMDict("JMdict_e.xml")

DRY_RUN = False  # Change to True to test without updating
PROGRESS_FILE = "progress.json"

from rich.table import Table


def choose_deck():
    decks = list_decks()

    table = Table(title="Available Decks")
    table.add_column("Index")
    table.add_column("Deck Name")

    for i, d in enumerate(decks):
        table.add_row(str(i), d)

    console.print(table)

    while True:
        choice = Prompt.ask("Select deck index")
        if choice.isdigit() and int(choice) < len(decks):
            return decks[int(choice)]


def save_progress(index, session_id, deck_name):
    data = {"last_index": index, "session_id": session_id, "deck_name": deck_name}
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return None
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def clear_progress():
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)


def is_pure_kana(text):
    return re.fullmatch(r"[ぁ-んァ-ンー]+", text) is not None


def contains_kanji(text):
    return re.search(r"[一-龯]", text) is not None


def format_front(kanji, reading):
    return f"{kanji}（{reading}）"


def process_note(note, session_id):
    note_id = note["noteId"]
    front = note["fields"]["Front"]["value"].strip()
    back = note["fields"]["Back"]["value"].strip()

    # Safety 1: Skip if already contains kanji
    if contains_kanji(front):
        return

    # Safety 2: Skip if not pure kana
    if not is_pure_kana(front):
        return

    candidates = jmdict.lookup(front)
    if not candidates:
        console.print(f"[yellow]No match:[/yellow] {front}")
        return

    ranked = rank_candidates(candidates, back)

    console.print(f"\n[bold]{front}[/bold] — {back}")

    # If only one viable kanji candidate
    valid = [c for score, c in ranked if c["kanji"]]
    if len(valid) == 1:
        kanji = valid[0]["kanji"][0]
        console.print(f"[green]Auto match:[/green] {kanji}")
        choice = Prompt.ask("Accept? (y/n)", default="y")
        if choice == "y":
            if not DRY_RUN:
                new_value = format_front(kanji, front)
                log_change(session_id, note_id, front, new_value)
                update_note(note_id, new_value)
        return

    # Ambiguous case
    for i, (score, cand) in enumerate(ranked[:5]):
        if not cand["kanji"]:
            continue
        console.print(f"{i}: {cand['kanji'][0]}  (score {score})")

    choice = Prompt.ask("Choose index or skip (s)", default="s")

    if choice.isdigit():
        idx = int(choice)
        kanji = ranked[idx][1]["kanji"][0]
        if not DRY_RUN:
            update_note(note_id, format_front(kanji, front))


def main():
    console.print("[bold cyan]Loading notes...[/bold cyan]")
    deck_name = choose_deck()
    console.print(f"[bold green]Selected deck:[/bold green] {deck_name}")

    note_ids = find_notes(deck_name)
    notes = get_notes(note_ids)

    progress = load_progress()

    if progress:
        resume = Prompt.ask(
            f"Resume session {progress['session_id']}? (y/n)", default="y"
        )
        if resume == "y":
            start_index = progress["last_index"]
            session_id = progress["session_id"]
            deck_name = progress["deck_name"]
        else:
            start_index = 0
            session_id = generate_session_id()
            deck_name = choose_deck()
    else:
        start_index = 0
        session_id = generate_session_id()
        deck_name = choose_deck()

    console.print(f"Session ID: {session_id}")
    console.print(f"Starting from card index {start_index}")

    try:
        for i in range(start_index, len(notes)):
            process_note(notes[i], session_id)
            save_progress(i + 1, session_id, deck_name)

    except KeyboardInterrupt:
        console.print("\n[red]Stopped safely.[/red]")
        console.print("You can resume later.")
        sys.exit(0)

    clear_progress()
    console.print("[green]Session complete.[/green]")


import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "rollback":
            sessions = get_sessions()
            print("Available sessions:")
            for s in sessions:
                print(f"- {s} ({len(sessions[s])} changes)")
            sid = input("Enter session ID to rollback: ")
            confirm = input(f"Confirm rollback of {sid}? (y/n): ")
            if confirm == "y":
                rollback_session(sid)
        else:
            print("Unknown command.")
    else:
        main()
