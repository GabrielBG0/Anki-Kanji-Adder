# similarity.py

from typing import Set

from rapidfuzz import fuzz

from normalization import meanings_to_set


def jaccard_similarity(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0

    return len(a & b) / len(a | b)


def token_overlap_score(a: Set[str], b: Set[str]) -> float:
    max_score = 0.0

    for x in a:
        tokens_x = set(x.split())
        if not tokens_x:
            continue

        for y in b:
            tokens_y = set(y.split())
            if not tokens_y:
                continue

            overlap = len(tokens_x & tokens_y)
            score = overlap / max(len(tokens_x), len(tokens_y))

            max_score = max(max_score, score)

    return max_score


def fuzzy_score(a: str, b_list: Set[str]) -> float:
    best = 0.0
    for b in b_list:
        best = max(best, fuzz.partial_ratio(a, b) / 100)
    return best


def gloss_score(english: str, glosses: list[str]) -> float:
    """
    Combined structural + fuzzy similarity.
    """

    eng_set = meanings_to_set(english)

    # JMDict glosses are already individual entries,
    # but we normalize them into a set as well.
    dict_set = set()
    for g in glosses:
        dict_set |= meanings_to_set(g)

    if not eng_set or not dict_set:
        return 0.0

    j_score = jaccard_similarity(eng_set, dict_set)
    t_score = token_overlap_score(eng_set, dict_set)
    f_score = fuzzy_score(english.lower(), dict_set)

    # Weighted blend
    return 0.5 * j_score + 0.3 * t_score + 0.2 * f_score
