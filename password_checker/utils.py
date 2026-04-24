"""Terminal color helpers."""

from __future__ import annotations

from colorama import Fore, Style


STRENGTH_COLORS = {
    "Weak": Fore.RED,
    "Medium": Fore.YELLOW,
    "Strong": Fore.GREEN,
    "Very Strong": Fore.CYAN,
}


def colorize_strength(text: str, strength: str) -> str:
    """Wrap text in a color that matches the strength level."""

    return f"{STRENGTH_COLORS.get(strength, Fore.WHITE)}{text}{Style.RESET_ALL}"


def colorize_status(text: str, passed: bool) -> str:
    """Color status text based on pass/fail state."""

    return f"{Fore.GREEN if passed else Fore.RED}{text}{Style.RESET_ALL}"