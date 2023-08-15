# biomarkerdash/utils.py

from typing import Tuple, Optional


def parse_reference_range(range_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse a reference range string and return a tuple (min, max)."""
    range_str = str(range_str).strip()  # Ensure the input is treated as a string
    if not range_str or range_str.lower() == 'nan':
        return None, None
    
    # If the reference range is a single number 0
    if range_str == '0':
        return 0.0, 0.0

    
    # For formats like "<5.7", "<130", etc.
    if range_str.startswith("<"):
        try:
            return None, float(range_str[1:])
        except ValueError:
            pass

    # For formats like ">5.7", ">130", etc.
    if range_str.startswith(">"):
        try:
            return float(range_str[1:]), None
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
        if len(parts) == 4 and parts[0] == '<':
            try:
                return None, float(parts[3])
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

    # For the special case format '-2.0 - +2.0'
    if range_str.startswith('-') and ' - +' in range_str:
        try:
            parts = range_str.split(' - +')
            min_val, max_val = float(parts[0]), float(parts[1])
            return min_val, max_val
        except ValueError:
            pass


    return None, None
