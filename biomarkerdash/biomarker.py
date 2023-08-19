# filename: biomarker.py
# Class to store biomarker metadata and time series data

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

import pandas as pd
from datetime import datetime
from typing import Optional, Tuple

from biomarkerdash.constants import (
    COLUMN_MARKER_NAME,
    COLUMN_DRAW_DATE,
    COLUMN_VALUE,
    COLUMN_MARKER_DESCRIPTION,
    COLUMN_UNIT,
)


class Biomarker:
    def __init__(
        self,
        name: str,
        description: str,
        unit: str,
        ref_range: Tuple[Optional[float], Optional[float]],
        history: Optional[pd.DataFrame] = None,
    ):
        """
        Initializes a Biomarker instance.

        Args:
        - name: Name of the biomarker.
        - description: Description for the biomarker.
        - category: Category for the biomarker.
        - unit: Unit of the biomarker value.
        - ref_range: Tuple of min and max reference values.
        - history: DataFrame containing time series data for the biomarker.
        """
        self.name = name
        self.description = description
        # TODO(@syler): implement categories
        # self.category = category
        self.unit = unit
        self.ref_range = ref_range
        self.history = history or pd.DataFrame(
            columns=[COLUMN_DRAW_DATE, COLUMN_VALUE]
        )

    def add_history_entry(self, draw_date_str: str, value: float, unit: str):
        """Add a single history entry to the biomarker."""
        # Parse the date string
        draw_date = datetime.strptime(draw_date_str, "%m/%d/%y")
        if str(unit) != "nan" and unit != self.unit:
            print(f"\nunit for {self.name} changed from {self.unit} to {unit}\n")
        self.history.loc[len(self.history)] = [draw_date, value]


def parse_row_to_biomarker(
    row: pd.Series, ref_range: Tuple[Optional[float], Optional[float]]
) -> Biomarker:
    """
    Parses a row of data to create a Biomarker object.

    Args:
    - row: A single row of the DataFrame containing biomarker details.
    - ref_range: Tuple of min and max reference values.

    Returns:
    - Biomarker instance.
    """
    name = row[COLUMN_MARKER_NAME].strip()
    # Assuming these columns exist in your CSV. Modify as needed.
    description = row.get(COLUMN_MARKER_DESCRIPTION, "")
    unit = row.get(COLUMN_UNIT, "")

    biomarker = Biomarker(name, description, unit, ref_range)
    return biomarker
