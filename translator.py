from __future__ import annotations

import logging
import re
from functools import lru_cache
from typing import Iterable

from deep_translator import GoogleTranslator

from cv_generator import CVData, LANGUAGES


logger = logging.getLogger(__name__)

TECH_TERMS = {
    "python",
    "java",
    "javascript",
    "sql",
    "mysql",
    "postgresql",
    "html",
    "css",
    "c++",
    "c#",
    "git",
    "github",
    "docker",
    "microsoft office",
    "excel",
    "powerpoint",
    "word",
    "3ds max",
    "autocad",
}

TEXT_FIELDS = [
    "degree_program",
    "current_education",
    "city",
    "marital_status",
    "experience",
    "education_details",
    "additional_education",
    "qualification",
]

LIST_FIELDS = [
    "professional_skills",
    "personal_qualities",
    "achievements",
    "additional_info",
]


def build_translations(data: CVData) -> dict[str, dict[str, str | list[str]]]:
    translations: dict[str, dict[str, str | list[str]]] = {}
    for language in LANGUAGES:
        values: dict[str, str | list[str]] = {}
        for field_name in TEXT_FIELDS:
            values[field_name] = translate_text(str(getattr(data, field_name)), language)
        for field_name in LIST_FIELDS:
            values[field_name] = translate_items(getattr(data, field_name), language)
        translations[language] = values
    return translations


def translate_items(items: Iterable[str], target: str) -> list[str]:
    return [translate_text(item, target) for item in items if item.strip()]


def translate_text(text: str, target: str) -> str:
    cleaned = text.strip()
    if not cleaned or cleaned == "-":
        return ""
    lines = [line.strip() for line in cleaned.splitlines()]
    translated_lines = [_translate_single_line(line, target) if line else "" for line in lines]
    return "\n".join(translated_lines)


@lru_cache(maxsize=2048)
def _translate_single_line(text: str, target: str) -> str:
    if _looks_non_translatable(text):
        return text
    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except Exception as exc:
        logger.warning("Translation failed for target=%s: %s", target, exc)
        return text


def _looks_non_translatable(text: str) -> bool:
    normalized = text.strip()
    if not normalized:
        return True
    has_letter = any(char.isalpha() for char in normalized)
    if not has_letter:
        return True
    if "@" in normalized and len(normalized.split()) <= 2:
        return True
    if _is_technical_term(normalized):
        return True
    return False


def _is_technical_term(text: str) -> bool:
    lowered = text.lower().strip()
    if lowered in TECH_TERMS:
        return True
    if re.fullmatch(r"[a-zA-Z0-9+#./ -]{1,28}", text) and any(char.isupper() for char in text):
        return True
    return False
