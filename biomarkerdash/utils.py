import re
import pandas as pd
from typing import Dict, Tuple, Optional


def parse_ref_range(range_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse a reference range string and return a tuple (min, max)."""

    # Ensure the input is treated as a string
    range_str = str(range_str).strip()  
    
    if not range_str or range_str.lower() == "nan":
        return None, None

    # Single number 0 pattern
    if range_str == "0":
        return 0.0, 0.0

    # Patterns
    patterns = [
        (r"^<([\d.]+)$", (None, 1)), # "<5.7", "<130", etc.
        (r"^>([\d.]+)$", (1, None)), # ">5.7", ">130", etc.
        (r"^> OR = ([\d.]+)$", (1, None)), # "> OR = 60", etc.
        (r"^< OR = ([\d.]+)$", (None, 1)), # "< OR = 60", etc.
        (r"^>=([\d.]+)$", (1, None)), # ">=125", etc.
        (r"^([\d.]+) OR LESS$", (None, 1)), # "0.2 OR LESS"
        (r"^([\d.-]+) - \+([\d.]+)$", (1, 2)), # "-2.0 - +2.0"
        (r"^([\d.-]+)-([\d.]+)$", (1, 2)), # standard "min-max" format
    ]

    for pattern, idx in patterns:
        match = re.match(pattern, range_str)
        if match:
            try:
                min = float(match.group(idx[0])) if idx[0] is not None else None
                max = float(match.group(idx[1])) if idx[1] is not None else None
                return min, max
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

        min, max = parse_ref_range(ref_range)
        if min is not None or max is not None:
            if marker_name in biomarker_to_range:
                existing_min, existing_max = biomarker_to_range[marker_name]
                # Update the reference range if the new one is different
                if existing_min != min or existing_max != max:
                    print(
                        f"Warning: Different reference range for {marker_name} "
                        f"on {row['Draw Date']}. "
                        f"Existing: {existing_min}-{existing_max}, "
                        f"New: {min}-{max}"
                        # f"\nCurrent ref range str: {ref_range}"
                    )
                    biomarker_to_range[marker_name] = (min, max)
            else:
                biomarker_to_range[marker_name] = (min, max)
        else:
            # couldn't parse min/max value
            print(
                f"Error parsing reference range for {marker_name} on "
                f"{row['Draw Date']} from '{ref_range}'"
                # f"\nmin: {min}"
                # f"\nmax: {max}"
            )

    return biomarker_to_range
