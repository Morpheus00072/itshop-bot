"""
WorldTravel v7.0 — Security filters.
"""
import re

_INJECTION_PATTERNS = [re.compile(p, re.I | re.U) for p in [
    r"(забудь|сбрось|игнорируй).*(инструкц|правил|промпт|роль)",
    r"(покажи|раскрой).*(промпт|инструкц|системн)",
    r"jailbreak|dan.?mode|developer mode",
    r"выйди из роли|break character",
    r"act as|roleplay as|pretend (you are|to be)",
]]

_BOSS_CMD_PATTERN = re.compile(
    r"\b(рассылка|broadcast|пауза бот|стоп бот|запустить бот|"
    r"добавить тур|удалить тур|изменить цену|история чатов|"
    r"покажи базу|select \*|drop table)\b",
    re.I | re.U
)


def is_injection(text: str) -> bool:
    return any(r.search(text) for r in _INJECTION_PATTERNS)


def is_boss_command_attempt(text: str) -> bool:
    return bool(_BOSS_CMD_PATTERN.search(text))