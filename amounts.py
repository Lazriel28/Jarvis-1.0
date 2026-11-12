from __future__ import annotations

from typing import Any, Optional, Tuple


def normalise_amount(value: Any) -> Optional[Tuple[float, str]]:
    """Return (amount, unit) parsed from a user value, or None.

    Accepts strings like "200 calories", "1 apple", "1.5 cups", or plain
    numbers. Units are lowercased and stripped. Unknown units are preserved
    as-is so downstream code can decide whether they are usable.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return (float(value), "servings")
    s = str(value).strip()
    if not s:
        return None
    parts = s.split(None, 1)
    try:
        amount = float(parts[0])
    except ValueError:
        return None
    unit = parts[1].strip().lower() if len(parts) > 1 else "servings"
    return (amount, unit)
