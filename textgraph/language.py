import re
from typing import Literal


Language = Literal["ru", "en"]


_RU_RE = re.compile(r"[а-яё]", re.IGNORECASE)
_EN_RE = re.compile(r"[a-z]", re.IGNORECASE)


def detect_token_language(token: str) -> Language:
    if _RU_RE.search(token):
        return "ru"
    return "en"


def detect_text_language(text: str) -> Language:
    ru_count = len(_RU_RE.findall(text))
    en_count = len(_EN_RE.findall(text))
    return "ru" if ru_count > en_count else "en"
