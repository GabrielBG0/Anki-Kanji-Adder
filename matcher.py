# matcher.py

from typing import Any, Dict, List, Tuple

from similarity import gloss_score


def rank_candidates(
    candidates: List[Dict[str, Any]],
    english: str,
) -> List[Tuple[float, Dict[str, Any]]]:
    """
    Returns:
        [(score, candidate_dict), ...]
    """

    scored: List[Tuple[float, Dict[str, Any]]] = []

    for c in candidates:
        score = gloss_score(english, c["glosses"])
        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)

    return scored
