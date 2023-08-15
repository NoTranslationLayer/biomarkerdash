import pandas as pd
from typing import Dict, Tuple, Optional


def parse_ref_range(range_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse a reference range string and return a tuple (min, max)."""
    range_str = str(
        range_str
    ).strip()  # Ensure the input is treated as a string
    if not range_str or range_str.lower() == "nan":
        return None, None

    # If the reference range is a single number 0
    if range_str == "0":
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
        if len(parts) == 4 and parts[0] == ">":
            try:
                return float(parts[3]), None
            except ValueError:
                pass
        if len(parts) == 4 and parts[0] == "<":
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
    if range_str.startswith("-") and " - +" in range_str:
        try:
            parts = range_str.split(" - +")
            min_val, max_val = float(parts[0]), float(parts[1])
            return min_val, max_val
        except ValueError:
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
                existing_min, existing_max = biomarker_to_range[marker_name]
                # Update the reference range if the new one is different
                if existing_min != min_val or existing_max != max_val:
                    print(
                        f"Warning: Different reference range for {marker_name} "
                        f"on {row['Draw Date']}. "
                        f"Existing: {existing_min}-{existing_max}, "
                        f"New: {min_val}-{max_val}"
                        # f"\nCurrent ref range str: {ref_range}"
                    )
                    biomarker_to_range[marker_name] = (min_val, max_val)
            else:
                biomarker_to_range[marker_name] = (min_val, max_val)
        else:
            # couldn't parse min/max value
            print(
                f"Error parsing reference range for {marker_name} on "
                f"{row['Draw Date']} from '{ref_range}'"
                # f"\nmin_val: {min_val}"
                # f"\nmax_val: {max_val}"
            )

    return biomarker_to_range
