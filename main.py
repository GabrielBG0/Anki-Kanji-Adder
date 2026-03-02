import re
from rich.console import Console
from rich.prompt import Prompt
from anki import find_notes, get_notes, update_note
from jmdict import JMDict
from matcher import rank_candidates

console = Console()
jmdict = JMDict("JMdict_e.xml")

DECK_NAME = "Japanese Vocabulary"
DRY_RUN = True  # Change to True to test without updating

def is_pure_kana(text):
    return re.fullmatch(r"[ぁ-んァ-ンー]+", text) is not None

def contains_kanji(text):
    return re.search(r"[一-龯]", text) is not None

def format_front(kanji, reading):
    return f"{kanji}（{reading}）"

def process_note(note):
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
                update_note(note_id, format_front(kanji, front))
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
    note_ids = find_notes(DECK_NAME)
    notes = get_notes(note_ids)

    console.print(f"Found {len(notes)} notes.\n")

    for note in notes:
        process_note(note)

if __name__ == "__main__":
    main()