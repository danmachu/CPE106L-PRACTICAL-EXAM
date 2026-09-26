"""
cli_helpers.py
Console input helpers. Every prompt loops until the value passes the
matching validation.py check, or the user types 'cancel' to abort the
action currently in progress.
"""

from datetime import date, datetime
from enum import Enum
from typing import Callable, Optional, Tuple, Type

CANCEL_KEYWORDS = {"cancel", "c"}


class InputCancelled(Exception):
    """Raised when the user types 'cancel' during a prompt sequence."""
    pass


def _check_cancel(raw: str) -> None:
    if raw.strip().lower() in CANCEL_KEYWORDS:
        raise InputCancelled()


def prompt_text(label: str, validator: Callable[[str], Tuple[bool, str]]) -> str:
    """validator(raw) -> (is_valid, error_message)"""
    while True:
        raw = input(f"{label}: ").strip()
        _check_cancel(raw)
        is_valid, message = validator(raw)
        if not is_valid:
            print(f"  ! {message} Try again (or type 'cancel').")
            continue
        return raw


def prompt_free_text(label: str, required: bool = False) -> str:
    while True:
        raw = input(f"{label}: ").strip()
        _check_cancel(raw)
        if required and raw == "":
            print(f"  ! {label} is required. Try again (or type 'cancel').")
            continue
        return raw


def prompt_date(label: str, validator: Optional[Callable[[date], Tuple[bool, str]]] = None) -> date:
    while True:
        raw = input(f"{label} (YYYY-MM-DD): ").strip()
        _check_cancel(raw)
        try:
            parsed = datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("  ! Invalid date format. Use YYYY-MM-DD. Try again (or type 'cancel').")
            continue
        if validator:
            is_valid, message = validator(parsed)
            if not is_valid:
                print(f"  ! {message} Try again (or type 'cancel').")
                continue
        return parsed


def prompt_optional_date(label: str) -> Optional[date]:
    while True:
        raw = input(f"{label} (YYYY-MM-DD, blank to skip): ").strip()
        _check_cancel(raw)
        if raw == "":
            return None
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("  ! Invalid date format. Use YYYY-MM-DD.")


def prompt_float(label: str, validator: Optional[Callable[[float], Tuple[bool, str]]] = None) -> float:
    while True:
        raw = input(f"{label}: ").strip()
        _check_cancel(raw)
        try:
            value = float(raw)
        except ValueError:
            print("  ! Must be a number. Try again (or type 'cancel').")
            continue
        if validator:
            is_valid, message = validator(value)
            if not is_valid:
                print(f"  ! {message} Try again (or type 'cancel').")
                continue
        return value


def prompt_enum(label: str, enum_class: Type[Enum]) -> Enum:
    options = list(enum_class)
    print(f"{label}:")
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option.value}")
    while True:
        raw = input("Choose a number (or 'cancel'): ").strip()
        _check_cancel(raw)
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print("  ! Invalid choice. Try again.")