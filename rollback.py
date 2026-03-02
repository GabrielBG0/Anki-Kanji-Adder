import json
from datetime import datetime

from anki import update_note

LOG_FILE = "rollback_log.jsonl"


def generate_session_id():
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def log_change(session_id, note_id, old_front, new_front):
    entry = {
        "session_id": session_id,
        "note_id": note_id,
        "old_front": old_front,
        "new_front": new_front,
        "timestamp": datetime.utcnow().isoformat(),
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_sessions():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f.readlines()]
    except FileNotFoundError:
        return {}

    sessions = {}
    for entry in lines:
        sessions.setdefault(entry["session_id"], []).append(entry)

    return sessions


def rollback_session(session_id):
    sessions = get_sessions()

    if session_id not in sessions:
        print("Session not found.")
        return

    entries = sessions[session_id]
    print(f"Reverting {len(entries)} changes from session {session_id}...")

    for entry in reversed(entries):
        update_note(entry["note_id"], entry["old_front"])

    print("Rollback complete.")
