import requests

ANKI_URL = "http://localhost:8765"


def list_decks():
    return invoke("deckNames")["result"]


def invoke(action, **params):
    return requests.post(
        ANKI_URL, json={"action": action, "version": 6, "params": params}
    ).json()


def find_notes(deck_name):
    query = f'deck:"{deck_name}"'
    return invoke("findNotes", query=query)["result"]


def get_notes(note_ids):
    return invoke("notesInfo", notes=note_ids)["result"]


def update_note(note_id, front_value):
    return invoke(
        "updateNoteFields", note={"id": note_id, "fields": {"Front": front_value}}
    )
