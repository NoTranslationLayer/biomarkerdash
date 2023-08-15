#!/usr/bin/env python3

import pandas as pd
import sys
import biomarkerdash.utils as util
import biomarkerdash.biomarker as bm
from typing import List, Dict, Optional, Tuple


def process_csv(csv_path: str) -> Dict[str, bm.Biomarker]:
    """
    Processes a CSV file and returns a dictionary of biomarkers.

    Args:
    - csv_path: Path to the CSV file.

    Returns:
    - Dictionary mapping marker names to Biomarker objects.
    """
    data = pd.read_csv(csv_path)

    # Extract the reference ranges
    biomarker_to_range = util.parse_wellnessfx_ref_ranges(data)

    biomarkers: Dict[str, bm.Biomarker] = {}

    for _, row in data.iterrows():
        marker_name = row["Marker Name"]

        if marker_name not in biomarkers:
            ref_range = biomarker_to_range.get(marker_name, (None, None))
            biomarkers[marker_name] = bm.parse_row_to_biomarker(row, ref_range)

        biomarkers[marker_name].add_history_entry(
            row["Draw Date"], row["Value"]
        )

    print(f"Biomarkers: {len(biomarkers.keys())}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 load_wellnessfx.py path_to_csv_file")
        sys.exit(1)

    csv_path: str = sys.argv[1]
    process_csv(csv_path)
