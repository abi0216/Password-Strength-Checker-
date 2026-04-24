"""Core password scoring and classification logic."""

from __future__ import annotations

import string


def analyze(password: str) -> dict[str, object]:
    """Return the pass/fail state, score, and strength for a password."""

    checks = {
        "min_length": len(password) >= 8,
        "preferred_length": len(password) >= 12,
        "uppercase": any(character.isupper() for character in password),
        "lowercase": any(character.islower() for character in password),
        "digit": any(character.isdigit() for character in password),
        "special": any(character in string.punctuation for character in password),
    }

    score_value = score(checks)

    return {
        "checks": checks,
        "score": score_value,
        "strength": classify(score_value),
    }


def score(checks: dict[str, bool]) -> int:
    """Count how many criteria passed."""

    return sum(checks.values())


def classify(score_value: int) -> str:
    """Map a numeric score to a strength label."""

    if score_value <= 2:
        return "Weak"
    if score_value == 3:
        return "Medium"
    if score_value <= 5:
        return "Strong"
    return "Very Strong"