import pandas as pd
from datetime import datetime
from typing import Optional, Tuple
import biomarkerdash.biomarker as bm


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
        self.history = history or pd.DataFrame(columns=["Draw Date", "Value"])

    def add_history_entry(self, draw_date_str: str, value: float):
        """Add a single history entry to the biomarker."""
        # Parse the date string
        draw_date = datetime.strptime(draw_date_str, "%m/%d/%y")
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
    name = row["Marker Name"]
    # Assuming these columns exist in your CSV. Modify as needed.
    description = row.get("Marker Description", "")
    unit = row.get("Units", "")

    biomarker = Biomarker(name, description, unit, ref_range)
    return biomarker
