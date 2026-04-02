import re
from typing import List, Optional, Tuple

from .language import detect_token_language


def simple_tokenize(text: str) -> List[str]:
    return re.findall(r"\b[\w$]+\b", text.lower())


def get_semantic_similarity(word1: str, word2: str, language: Optional[str] = None) -> float:
    w1, w2 = word1.lower(), word2.lower()
    if w1 == w2:
        return 1.0

    synonyms_en = {
        "company": ["firm", "corporation", "business"],
        "firm": ["company", "corporation", "business"],
        "launched": ["released", "started", "began"],
        "released": ["launched", "issued", "published"],
        "product": ["item", "goods", "merchandise"],
        "developed": ["created", "made", "built"],
        "cost": ["price", "value", "worth"],
        "quickly": ["fast", "rapidly", "swiftly"],
        "stood": ["rose"],
        "walked": ["went", "left"],
    }

    synonyms_ru = {
        "компания": ["фирма", "корпорация", "бизнес"],
        "фирма": ["компания", "корпорация", "бизнес"],
        "запустила": ["выпустила", "начала"],
        "выпустила": ["запустила", "опубликовала"],
        "продукт": ["товар", "изделие"],
        "разработанный": ["созданный"],
        "быстро": ["оперативно", "скорее"],
        "вчера": ["накануне"],
        "мужчина": ["человек", "мужик"],
        "ушел": ["удалился", "покинул"],
    }

    if language is None:
        language = "ru" if detect_token_language(w1) == "ru" or detect_token_language(w2) == "ru" else "en"
    synonyms = synonyms_ru if language == "ru" else synonyms_en

    if w1 in synonyms and w2 in synonyms[w1]:
        return 0.85
    if w2 in synonyms and w1 in synonyms[w2]:
        return 0.85

    set1, set2 = set(w1), set(w2)
    if set1 and set2:
        jaccard = len(set1 & set2) / len(set1 | set2)
        if jaccard > 0.6:
            return 0.65
    return 0.0


def align_tokens(original_tokens: List[str], edited_tokens: List[str], language: Optional[str] = None) -> List[Tuple]:
    alignments = []
    used_edited = set()

    for i, orig in enumerate(original_tokens):
        best_match = None
        best_sim = 0.0
        for j, edit in enumerate(edited_tokens):
            if j in used_edited:
                continue
            sim = get_semantic_similarity(orig, edit, language=language)
            if sim > best_sim and sim >= 0.4:
                best_sim = sim
                best_match = j

        if best_match is not None:
            alignments.append((i, orig, best_match, edited_tokens[best_match], best_sim))
            used_edited.add(best_match)
        else:
            alignments.append((i, orig, None, None, 0.0))

    for j, edit in enumerate(edited_tokens):
        if j not in used_edited:
            alignments.append((None, None, j, edit, 0.0))

    return alignments
