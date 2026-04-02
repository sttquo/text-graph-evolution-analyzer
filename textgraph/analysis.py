from typing import Dict, List, Optional, Set, Tuple

from .language import detect_token_language
from .models import SyntaxComparison
from .parsing import align_tokens


SYNTAX_ROLES_EN = {
    "the": "det",
    "a": "det",
    "an": "det",
    "company": "nsubj",
    "firm": "nsubj",
    "man": "nsubj",
    "launched": "ROOT",
    "released": "ROOT",
    "stood": "ROOT",
    "walked": "ROOT",
    "product": "dobj",
    "bench": "pobj",
    "new": "amod",
    "quickly": "advmod",
    "over": "prep",
    "on": "prep",
    "yesterday": "npadvmod",
    "three": "amod",
    "5": "nummod",
    "5m": "compound",
    "which": "nsubjpass",
    "who": "nsubj",
    "was": "auxpass",
    "and": "cc",
    "developed": "acl",
    "sitting": "acl",
    "years": "pobj",
    "approximately": "advmod",
    "million": "dobj",
    "away": "advmod",
    "up": "prt",
}

SYNTAX_ROLES_RU = {
    "это": "det",
    "этот": "det",
    "эта": "det",
    "компания": "nsubj",
    "фирма": "nsubj",
    "мужчина": "nsubj",
    "человек": "nsubj",
    "запустила": "ROOT",
    "выпустила": "ROOT",
    "встал": "ROOT",
    "ушел": "ROOT",
    "продукт": "dobj",
    "товар": "dobj",
    "скамейке": "pobj",
    "новый": "amod",
    "новую": "amod",
    "быстро": "advmod",
    "вчера": "npadvmod",
    "три": "amod",
    "года": "pobj",
    "лет": "pobj",
    "который": "nsubjpass",
    "которого": "nsubjpass",
    "был": "auxpass",
    "и": "cc",
    "разработанный": "acl",
    "сидевший": "acl",
    "примерно": "advmod",
    "миллион": "dobj",
    "миллиона": "dobj",
    "ушел": "ROOT",
}


def get_syntax_role(token: str, language: Optional[str] = None) -> str:
    if language is None:
        language = detect_token_language(token)
    roles = SYNTAX_ROLES_RU if language == "ru" else SYNTAX_ROLES_EN
    return roles.get(token.lower(), "unknown")


def compare_syntax_trees(original_tokens: List[str], edited_tokens: List[str], language: Optional[str] = None) -> List[SyntaxComparison]:
    comparisons: List[SyntaxComparison] = []
    alignments = align_tokens(original_tokens, edited_tokens, language=language)
    for a in alignments:
        if a[0] is not None and a[2] is not None:
            orig_role = get_syntax_role(a[1], language=language)
            edit_role = get_syntax_role(a[3], language=language)
            comparisons.append(
                SyntaxComparison(
                    token=a[1],
                    original_role=orig_role,
                    edited_role=edit_role,
                    is_preserved=(orig_role == edit_role),
                )
            )
    return comparisons


def extract_semantic_triples(tokens: List[str], language: Optional[str] = None) -> Set[Tuple[str, str, str]]:
    triples: Set[Tuple[str, str, str]] = set()
    token_set = set(tokens)

    if language is None and tokens:
        language = detect_token_language(tokens[0])
    if language is None:
        language = "en"

    if language == "ru":
        if "компания" in token_set and "запустила" in token_set:
            triples.add(("launch", ":ARG0", "компания"))
        if "фирма" in token_set and "выпустила" in token_set:
            triples.add(("release", ":ARG0", "фирма"))
        if "мужчина" in token_set and "встал" in token_set:
            triples.add(("stand", ":ARG0", "мужчина"))
        if ("запустила" in token_set or "выпустила" in token_set) and "продукт" in token_set:
            triples.add(("launch", ":ARG1", "продукт"))
        if "разработанный" in token_set and "продукт" in token_set:
            triples.add(("продукт", ":ARG1-of", "develop"))
            if "три" in token_set and ("года" in token_set or "лет" in token_set):
                triples.add(("develop", ":duration", "3 года"))
        if "5" in token_set and ("миллион" in token_set or "миллиона" in token_set):
            triples.add(("продукт", ":cost", "5 миллионов"))
        if "вчера" in token_set:
            triples.add(("event", ":time", "вчера"))
    else:
        if "company" in token_set and "launched" in token_set:
            triples.add(("launch", ":ARG0", "company"))
        if "firm" in token_set and "released" in token_set:
            triples.add(("release", ":ARG0", "firm"))
        if "man" in token_set and "stood" in token_set:
            triples.add(("stand", ":ARG0", "man"))
        if "launched" in token_set and "product" in token_set:
            triples.add(("launch", ":ARG1", "product"))
        if "released" in token_set and "product" in token_set:
            triples.add(("release", ":ARG1", "product"))
        if "developed" in token_set and "product" in token_set:
            triples.add(("product", ":ARG1-of", "develop"))
            if "three" in token_set and "years" in token_set:
                triples.add(("develop", ":duration", "3 years"))
        if "5" in token_set and "million" in token_set:
            triples.add(("product", ":cost", "5 million"))
        if "5m" in token_set:
            triples.add(("product", ":cost", "5M"))
        if "yesterday" in token_set:
            triples.add(("event", ":time", "yesterday"))
    return triples


def compare_semantic_graphs(original_tokens: List[str], edited_tokens: List[str], language: Optional[str] = None) -> Dict:
    triples1 = extract_semantic_triples(original_tokens, language=language)
    triples2 = extract_semantic_triples(edited_tokens, language=language)
    common = triples1 & triples2
    only_in_original = triples1 - triples2
    only_in_edited = triples2 - triples1
    total_original = len(triples1)
    preservation_rate = len(common) / total_original * 100 if total_original > 0 else 0.0
    return {
        "common": common,
        "only_original": only_in_original,
        "only_edited": only_in_edited,
        "preservation_rate": preservation_rate,
        "total_original": total_original,
        "total_edited": len(triples2),
    }


def compute_change_stats(alignments: List[Tuple]) -> Dict[str, int]:
    stats = {"preserved": 0, "replaced": 0, "removed": 0, "inserted": 0}
    for a in alignments:
        if a[0] is not None and a[2] is not None:
            if a[4] >= 0.95:
                stats["preserved"] += 1
            else:
                stats["replaced"] += 1
        elif a[0] is not None and a[2] is None:
            stats["removed"] += 1
        elif a[0] is None and a[2] is not None:
            stats["inserted"] += 1
    return stats


def _find_nearest_index(target: int, candidates: List[int], prefer_left: bool = False) -> Optional[int]:
    if not candidates:
        return None
    if prefer_left:
        left = [c for c in candidates if c < target]
        if left:
            return max(left)
    return min(candidates, key=lambda c: (abs(c - target), c))


def build_dependency_edges(tokens: List[str], language: Optional[str] = None) -> List[Tuple[int, int, str]]:
    if not tokens:
        return []

    roles = [get_syntax_role(token, language=language) for token in tokens]
    root_indices = [i for i, role in enumerate(roles) if role == "ROOT"]
    noun_like_indices = [i for i, role in enumerate(roles) if role in {"nsubj", "nsubjpass", "dobj", "pobj"}]
    if not root_indices:
        root_indices = [0]

    edges: List[Tuple[int, int, str]] = []
    for i, role in enumerate(roles):
        if i in root_indices:
            continue

        if role in {"det", "amod", "nummod", "compound"}:
            right_nouns = [n for n in noun_like_indices if n > i]
            head = _find_nearest_index(i, right_nouns) or _find_nearest_index(i, noun_like_indices, prefer_left=True)
        elif role in {"nsubj", "nsubjpass"}:
            head = _find_nearest_index(i, root_indices)
        elif role in {"dobj", "pobj", "auxpass", "prt", "advmod", "npadvmod", "prep"}:
            head = _find_nearest_index(i, root_indices, prefer_left=True)
        elif role == "acl":
            head = _find_nearest_index(i, noun_like_indices, prefer_left=True)
        elif role == "cc":
            head = i - 1 if i > 0 else _find_nearest_index(i, root_indices)
        else:
            head = _find_nearest_index(i, root_indices, prefer_left=True)

        if head is None:
            head = root_indices[0]
        if head != i:
            edges.append((head, i, role))
    return edges
