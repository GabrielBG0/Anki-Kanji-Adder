# normalization.py

import re
import unicodedata
from typing import List, Set

NUMBERING_PATTERN = re.compile(r"\b\d+[\.\)]\s*")
WHITESPACE_PATTERN = re.compile(r"\s+")
PAREN_PATTERN = re.compile(r"\(.*?\)")


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()

    # Remove numbering like "1." or "2)"
    text = NUMBERING_PATTERN.sub("", text)

    # Remove "to " prefix (verbs)
    text = re.sub(r"^to\s+", "", text)

    text = WHITESPACE_PATTERN.sub(" ", text)

    return text.strip()


def split_meanings(gloss: str) -> List[str]:
    gloss = normalize_text(gloss)

    parts = re.split(r"[;/,]", gloss)

    cleaned = []

    for part in parts:
        part = part.strip()
        part = PAREN_PATTERN.sub("", part).strip()

        if part:
            cleaned.append(part)

    return cleaned


def meanings_to_set(gloss: str) -> Set[str]:
    return set(split_meanings(gloss))
