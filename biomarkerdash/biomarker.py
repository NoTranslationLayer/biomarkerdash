import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from typing import List, Dict, Optional, Tuple


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

    def plot_history(self):
        """Generate an interactive plot of the biomarker's history."""
        dates = self.history["Draw Date"].tolist()
        # Convert values to numpy array
        values = np.array(self.history["Value"], dtype=float)

        # Determine colors for each point based on reference range
        def determine_color(value, ref_range):
            min_val, max_val = ref_range
            if min_val is not None and max_val is not None:
                return "green" if min_val <= value <= max_val else "red"
            elif min_val is not None:
                return "green" if value >= min_val else "red"
            elif max_val is not None:
                return "green" if value <= max_val else "red"
            else:  # No reference range present
                return "grey"

        # Get colors based on reference range
        colors = [determine_color(val, self.ref_range) for val in values]

        fig = go.Figure()

        # Add a grey line to connect points
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode="lines",
                line=dict(color="lightgrey"),
                name="Values",
            )
        )

        # Add points with colors based on reference range
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode="markers",
                marker=dict(color=colors, size=10),
                name="Values",
            )
        )

        fig.update_layout(
            title=f"History of {self.name}",
            xaxis_title="Date",
            yaxis_title=f"Value ({self.unit})",
        )
        fig.show()


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
    description = row.get("Description", "")
    unit = row.get("Units", "")

    biomarker = Biomarker(name, description, unit, ref_range)
    return biomarker
