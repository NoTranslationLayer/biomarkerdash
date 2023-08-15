import re
import pandas as pd
from typing import Dict, Tuple, Optional


def parse_ref_range(range_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse a reference range string and return a tuple (min_val, max_val)."""

    # Ensure the input is treated as a string
    range_str = str(range_str).strip()

    if not range_str or range_str.lower() == "nan":
        return None, None

    # Single number 0 pattern
    if range_str == "0":
        return 0.0, 0.0

    # Patterns
    patterns = [
        (r"^<([\d.]+)$", (None, 1)),  # "<5.7", "<130", etc.
        (r"^>([\d.]+)$", (1, None)),  # ">5.7", ">130", etc.
        (r"^> OR = ([\d.]+)$", (1, None)),  # "> OR = 60", etc.
        (r"^< OR = ([\d.]+)$", (None, 1)),  # "< OR = 60", etc.
        (r"^>=([\d.]+)$", (1, None)),  # ">=125", etc.
        (r"^([\d.]+) OR LESS$", (None, 1)),  # "0.2 OR LESS"
        (r"^([\d.-]+) - \+([\d.]+)$", (1, 2)),  # "-2.0 - +2.0"
        (r"^([\d.-]+)-([\d.]+)$", (1, 2)),  # standard "min_val-max_val" format
    ]

    for pattern, idx in patterns:
        m = re.match(pattern, range_str)
        if m:
            try:
                min_v = float(m.group(idx[0])) if idx[0] is not None else None
                max_v = float(m.group(idx[1])) if idx[1] is not None else None
                return min_v, max_v
            except (ValueError, IndexError):
                pass

    return None, None


def parse_wellnessfx_ref_ranges(
    data: pd.DataFrame,
) -> Dict[str, Tuple[Optional[float], Optional[float]]]:
    """
    Parse the data from the WellnessFX exported CSV to return a dictionary
    mapping marker names to their reference ranges.
    """
    biomarker_to_range: Dict[str, Tuple[Optional[float], Optional[float]]] = {}

    for _, row in data.iterrows():
        marker_name: str = row["Marker Name"]
        ref_range: str = row["Reference Range"]
        if str(ref_range).strip().lower() == "nan":
            ref_range = ""

        if not ref_range:
            # no reference range data for this entry
            continue

        min_val, max_val = parse_ref_range(ref_range)
        if min_val is not None or max_val is not None:
            if marker_name in biomarker_to_range:
                existing_min_val, existing_max_val = biomarker_to_range[
                    marker_name
                ]
                # Update the reference range if the new one is different
                if existing_min_val != min_val or existing_max_val != max_val:
                    print(
                        f"Warning: Different reference range for {marker_name} "
                        f"on {row['Draw Date']}. "
                        f"Existing: {existing_min_val}-{existing_max_val}, "
                        f"New: {min_val}-{max_val}"
                        # f"\nCurrent ref range str: {ref_range}"
                    )
                    biomarker_to_range[marker_name] = (min_val, max_val)
            else:
                biomarker_to_range[marker_name] = (min_val, max_val)
        else:
            # couldn't parse min_val/max_val value
            print(
                f"Error parsing reference range for {marker_name} on "
                f"{row['Draw Date']} from '{ref_range}'"
                # f"\nmin_val: {min_val}"
                # f"\nmax_val: {max_val}"
            )

    return biomarker_to_range
