#!/usr/bin/env python3

import pandas as pd
import sys
import biomarkerdash.utils as util


def process_csv(csv_path: str) -> None:
    # Load the CSV data
    data = pd.read_csv(csv_path)

    # Extract the reference ranges
    biomarker_to_range = util.parse_wellnessfx_reference_ranges(data)
    print("Processing complete!")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 load_wellnessfx.py path_to_csv_file")
        sys.exit(1)

    csv_path: str = sys.argv[1]
    process_csv(csv_path)
