# Anki Kanji Adder

A CLI tool that augments Japanese vocabulary Anki decks by automatically adding kanji to kana-only cards using **JMdict** and intelligent English meaning matching.

The program provides a Tinder-like interactive interface where you can:

* Accept automatic matches
* Choose between ambiguous candidates
* Skip entries
* Resume sessions safely
* Roll back changes if necessary

---

## ✨ Features

* 🔎 Kana → Kanji matching using JMdict
* 🧠 Intelligent English gloss normalization
* 📊 Structural similarity scoring (Jaccard + token overlap + fuzzy match)
* 🎯 Handles multi-meaning cards
* 💾 Session logging and rollback support
* ▶ Resume interrupted sessions
* 🧪 Dry-run mode for safe testing
* 📚 Deck selection from Anki

---

## 📦 Requirements

* Linux
* Python 3.10+
* Anki desktop running
* AnkiConnect plugin installed

### Install AnkiConnect

In Anki:

```
Tools → Add-ons → Get Add-ons
```

Install:

```
2055492159
```

Restart Anki.

---

## 📘 JMdict Setup

Download **JMdict_e.xml** from:

[https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project](https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project)

Download:

> “The current version (Unicode UTF8)”

Place the file in your project root:

```
Anki-Kanji-Adder/
    JMdict_e.xml
```

---

## 🚀 Installation (Using uv)

Inside your project directory:

```bash
uv init
uv add requests rich rapidfuzz
```

---

## 🛠 Usage

Make sure:

* Anki is open
* AnkiConnect is enabled
* JMdict_e.xml exists in project root

Run:

```bash
uv run main.py
```

You will:

1. Select a deck
2. Review matches interactively
3. Accept, reject, or choose candidates

---

## 📝 Card Format

If accepted, cards are reformatted as:

```
Front: 食べる（たべる）
Back: eat
```

The program only modifies cards where:

* Front contains pure kana
* Front does not already contain kanji

---

## 🧠 Matching Strategy

The ranking system uses:

* English gloss normalization
* Multi-meaning splitting
* Jaccard similarity
* Token-level overlap
* Fuzzy matching (RapidFuzz)

This allows correct handling of entries like:

```
important; significant; serious; crucial
1. impossible
2. unreasonable; unjustifiable
```

---

## 🛑 Dry Run Mode

In `main.py`:

```python
DRY_RUN = True
```

Set to `False` to actually update cards.

---

## 💾 Resume Support

If interrupted (Ctrl+C), progress is saved automatically.

When restarting, you will be prompted to resume.

---

## 🔁 Rollback Changes

All changes are logged per session.

To rollback:

```bash
uv run main.py rollback
```

You will see available sessions and can revert any of them safely.

---

## 📂 Project Structure

```
anki.py          # AnkiConnect wrapper
jmdict.py        # JMdict XML indexer
normalization.py # English gloss normalization
similarity.py    # Similarity scoring logic
matcher.py       # Candidate ranking
main.py          # CLI interface
rollback.py      # Session logging and rollback
```

---

## ⚠ Limitations

* Only works for kana → kanji upgrades
* Assumes English meanings are reasonably accurate
* Does not handle grammar disambiguation beyond gloss similarity

---

## 📜 License

JMdict is distributed under its own license.
Refer to the JMdict license for redistribution details.

This project is for personal learning and automation purposes.

---

## 👤 Author

Gabriel B. Gutierrez
© 2026

GitHub: [https://github.com/GabrielBG0/Anki-Kanji-Adder](https://github.com/GabrielBG0/Anki-Kanji-Adder)

