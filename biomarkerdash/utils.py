# biomarkerdash/utils.py

from typing import Tuple, Optional


def parse_reference_range(range_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse a reference range string and return a tuple (min, max)."""
    range_str = str(range_str)  # Ensure the input is treated as a string
    if not range_str:
        return None, None
    if "-" in range_str:
        try:
            min_val, max_val = map(float, range_str.split("-"))
            return min_val, max_val
        except ValueError:
            return None, None
    if "OR" in range_str and "=" in range_str:
        parts = range_str.split()
        if len(parts) == 4 and parts[0] in ['>', '<']:
            try:
                return (float(parts[1]), None) if parts[0] == '>' else (None, float(parts[1]))
            except ValueError:
                return None, None
    return None, None
