#!/usr/bin/env python3

import pandas as pd
import sys
from biomarkerdash.utils import parse_reference_range
from typing import Dict, Optional, Tuple


def process_csv(csv_path: str) -> None:
    # Load the CSV data
    data = pd.read_csv(csv_path)

    # Map for storing test names and their reference ranges
    biomarker_to_range: Dict[str, Tuple[Optional[float], Optional[float]]] = {}

    for _, row in data.iterrows():
        marker_name: str = row["Marker Name"]
        ref_range: str = row["Reference Range"]
        if str(ref_range).strip().lower() == "nan":
            ref_range = ""

        # Check and parse the reference range
        min_val, max_val = parse_reference_range(ref_range)
        if min_val is None and max_val is None and ref_range:
            print(
                f"Error parsing reference range for {marker_name} on "
                f"{row['Draw Date']} from '{ref_range}'"
                # f"\nmin_val: {min_val}"
                # f"\nmax_val: {max_val}"
            )

        # Check against the stored reference range for this biomarker
        if marker_name in biomarker_to_range:
            existing_min, existing_max = biomarker_to_range[marker_name]
            if (min_val is not None or max_val is not None) and (existing_min != min_val or existing_max != max_val):
                print(
                    f"Warning: Different reference range for {marker_name} "
                    f"on {row['Draw Date']}. "
                    f"Existing: {existing_min}-{existing_max}, "
                    f"New: {min_val}-{max_val}"
                )
                biomarker_to_range[marker_name] = (min_val, max_val)
        else:
            # Only store the new reference range if it's not (None, None)
            if min_val is not None or max_val is not None:
                biomarker_to_range[marker_name] = (min_val, max_val)

    print("Processing complete!")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 load_wellnessfx.py path_to_csv_file")
        sys.exit(1)

    csv_path: str = sys.argv[1]
    process_csv(csv_path)
