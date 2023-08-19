# filename: utils.py
# Utilities for parsing and I/O

# Copyright (c) 2023, No Translation Layer LLC
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import re
import pandas as pd
from typing import Dict, Tuple, Optional

import biomarkerdash.biomarker as bm
from biomarkerdash.constants import (
    COLUMN_MARKER_NAME,
    COLUMN_REFERENCE_RANGE,
    COLUMN_DRAW_DATE,
    COLUMN_VALUE,
    COLUMN_UNIT,
)


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
        marker_name: str = row[COLUMN_MARKER_NAME]
        unit: str = row[COLUMN_UNIT]
        ref_range: str = row[COLUMN_REFERENCE_RANGE]
        if str(ref_range).strip().lower() == "nan":
            ref_range = ""

        if not ref_range:
            # no reference range data for this entry
            continue

        min_val, max_val = parse_ref_range(ref_range)

        # For absolute white blood cell counts, the unit is expressed as x1000
        # count per microliter, but some of the reference ranges are expressed
        # in count per microliter (without the x1000 multiplier). Sanity check
        # for consistency here and update the reference ranges to match if
        # needed.
        # e.g. a (value, unit, ref_range) of:
        # (0.673, x10E3/uL, 850-3900) would get adjusted to:
        # (0.673, x10E3/uL, 0.85-3.9)
        if str(unit) != "nan" and "x10E3" in unit:
            # This discrepancy is only found in Quest white blood cell counts,
            # not platelet count, so don't apply the correction for platelet
            # count
            if marker_name != "Platelet Count":
                # Use a hardcoded threshold of 100 to determine whether or not
                # the scaling needs to be applied, or if the order of magnitude
                # is already correct. For white blood cell counts expressed in
                # x10E3/u, the upper limit of the reference range always falls
                # below 100.
                if max_val is not None and max_val >= 100:
                    print(
                        f"Warning: Correcting reference range ({min_val}, "
                        f"{max_val}) {unit} for {marker_name} to "
                        f"({min_val / 1000 if min_val is not None else None}, "
                        f"{max_val / 1000}) {unit} "
                    )
                    max_val = max_val / 1000
                    if min_val is not None:
                        min_val = min_val / 1000

        if min_val is not None or max_val is not None:
            if marker_name in biomarker_to_range:
                existing_min_val, existing_max_val = biomarker_to_range[
                    marker_name
                ]
                # Update the reference range if the new one is different
                if existing_min_val != min_val or existing_max_val != max_val:
                    print(
                        f"Warning: Different reference range for {marker_name} "
                        f"on {row[COLUMN_DRAW_DATE]}. "
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
                f"{row[COLUMN_DRAW_DATE]} from '{ref_range}'"
                # f"\nmin_val: {min_val}"
                # f"\nmax_val: {max_val}"
            )

    return biomarker_to_range


def load_wellnessfx_biomarkers(csv_path: str) -> Dict[str, bm.Biomarker]:
    """
    Processes a CSV file and returns a dictionary of biomarkers.

    Args:
    - csv_path: Path to the CSV file.

    Returns:
    - Dictionary mapping marker names to Biomarker objects.
    """
    data = pd.read_csv(csv_path, dtype={COLUMN_UNIT: str})

    # Trim unnecessary whitespace in column names
    data.columns = [col.strip() for col in data.columns]

    # Replace Unicode 63 (which is "?") with Unicode 956 (which is "µ") for the unit column
    data[COLUMN_UNIT] = data[COLUMN_UNIT].str.replace(chr(63), chr(956))

    # Extract the reference ranges
    biomarker_to_range = parse_wellnessfx_ref_ranges(data)

    biomarkers: Dict[str, bm.Biomarker] = {}

    for _, row in data.iterrows():
        marker_name = row[COLUMN_MARKER_NAME]

        if marker_name not in biomarkers:
            ref_range = biomarker_to_range.get(marker_name, (None, None))
            biomarkers[marker_name] = bm.parse_row_to_biomarker(row, ref_range)

        biomarkers[marker_name].add_history_entry(
            row[COLUMN_DRAW_DATE], row[COLUMN_VALUE], row[COLUMN_UNIT]
        )

    print(f"Loaded {len(biomarkers.keys())} biomarkers")
    return biomarkers


def generate_filename(marker_name: str) -> str:
    """
    Generate an appropriate filename by removing or replacing certain
    characters.

    Args:
    - marker_name (str): The original marker name.

    Returns:
    - str: A sanitized filename.
    """

    # Define characters to be replaced and their replacements
    replacements = {
        " ": "_",  # replace spaces with underscores
        "%": "pct",  # replace '%' with 'pct'
    }

    # Characters to be removed
    remove_chars = "(),:/"

    # Combine replacements and removals into one dictionary
    translation_dict = {
        **replacements,
        **{char: None for char in remove_chars},
    }

    # Apply the translation
    marker_name = marker_name.translate(str.maketrans(translation_dict))

    return marker_name + ".html"
