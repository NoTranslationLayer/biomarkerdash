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
        draw_date = datetime.strptime(draw_date_str, '%m/%d/%y')
        self.history.loc[len(self.history)] = [draw_date, value]

    def plot_history(self):
        """Generate an interactive time series plot of the biomarker history using Plotly."""

        # Create the figure
        fig = go.Figure()

        # Add a scatter plot of the draw date vs value
        fig.add_trace(go.Scatter(
            x=self.history['Draw Date'], 
            y=self.history['Value'], 
            mode='lines+markers',
            name=self.name
        ))

        # Set layout properties
        fig.update_layout(
            title=f"History of {self.name}",
            xaxis_title="Draw Date",
            yaxis_title=self.unit,
            xaxis=dict(type='date')
        )

        # Display the plot
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
    unit = row.get("Unit", "")

    biomarker = Biomarker(name, description, unit, ref_range)
    return biomarker
