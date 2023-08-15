# biomarkerdash/utils.py

from typing import Tuple, Optional


def parse_reference_range(range_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse a reference range string and return a tuple (min, max)."""
    range_str = str(range_str).strip()  # Ensure the input is treated as a string
    if not range_str or range_str.lower() == 'nan':
        return None, None
    
    # For formats like "<5.7", "<130", etc.
    if range_str.startswith("<"):
        try:
            return None, float(range_str[1:])
        except ValueError:
            pass

    # For formats like "> OR = 60", ">=125", etc.
    if "OR" in range_str and "=" in range_str:
        parts = range_str.split()
        if len(parts) == 4 and parts[0] == '>':
            try:
                return float(parts[3]), None
            except ValueError:
                pass
    elif range_str.startswith(">="):
        try:
            return float(range_str[2:]), None
        except ValueError:
            pass

    # For formats like "0.2 OR LESS"
    if "OR LESS" in range_str:
        try:
            return None, float(range_str.split()[0])
        except ValueError:
            pass
    
    # Standard range format "min-max"
    if "-" in range_str:
        try:
            min_val, max_val = map(float, range_str.split("-"))
            return min_val, max_val
        except ValueError:
            pass

    return None, None
