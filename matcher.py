from rapidfuzz import fuzz


def normalize(text):
    return text.lower().replace("to ", "").strip()


def rank_candidates(candidates, english):
    english = normalize(english)
    scored = []

    for c in candidates:
        best = 0
        for gloss in c["glosses"]:
            score = fuzz.partial_ratio(english, gloss)
            best = max(best, score)

        scored.append((best, c))

    scored.sort(reverse=True, key=lambda x: x[0])
    return scored
