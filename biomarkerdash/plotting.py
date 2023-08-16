import numpy as np
import plotly.graph_objects as go
import plotly.offline as pyo
from typing import List, Dict, Optional, Tuple
import biomarkerdash.biomarker as bm


def determine_color(
    value: float, ref_range: Tuple[Optional[float], Optional[float]]
) -> str:
    """
    Determine color for a given value based on a reference range.

    Parameters:
    - value (float): The value for which the color is determined.
    - ref_range (Tuple[Optional[float], Optional[float]]): Tuple containing the
    minimum and maximum values of the reference range.

    Returns:
    - str: A color string based on where the value falls within the reference
    range.
    """
    min_val, max_val = ref_range
    green = "rgb(82, 182, 2)"
    red = "rgb(236, 2, 0)"
    if min_val is not None and max_val is not None:
        return green if min_val <= value <= max_val else red
    elif min_val is not None:
        return green if value >= min_val else red
    elif max_val is not None:
        return green if value <= max_val else red
    else:  # No reference range present
        return "grey"


def plot_history(marker: bm.Biomarker, save_to: str) -> None:
    """
    Generate an interactive plot of the biomarker's history.

    The method uses the history and reference range of the biomarker instance to generate the plot.
    The method is part of the Biomarker class.
    """
    dates = marker.history["Draw Date"].tolist()
    values = marker.history["Value"].tolist()
    try:
        values = np.array(values, dtype=float)
    except ValueError:
        print(f"Failed to extract numerical values for {marker.name}")
        return

    # Get colors based on reference range
    colors = [determine_color(val, marker.ref_range) for val in values]

    fig = go.Figure()

    # Add a grey line to connect points
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=values,
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0.15)"),
        )
    )

    # Add points with colors based on reference range
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=values,
            mode="markers",
            marker=dict(
                color=colors, size=10, line=dict(color="white", width=1)
            ),
        )
    )

    min_val, max_val = marker.ref_range

    # Determine the data range
    data_min = min(values)
    data_max = max(values)

    # Define a buffer for y-axis (e.g., 10% of max_val)
    buffer = 0.1 * (max_val if max_val is not None else data_max)

    # Determine the overall y-axis range
    y_range = [
        min(
            min_val - buffer if min_val is not None else data_min,
            data_min - buffer,
        ),
        max(
            max_val + buffer if max_val is not None else data_max,
            data_max + buffer,
        ),
    ]
    shapes = []

    # Color areas outside the reference range
    if min_val is not None:
        shapes.append(
            dict(
                type="rect",
                xref="paper",
                x0=0,
                x1=1,
                y0=y_range[0],
                y1=min_val,
                fillcolor="rgba(236,2,0,0.2)",
                layer="below",
                line=dict(width=0),
            )
        )

    if max_val is not None:
        shapes.append(
            dict(
                type="rect",
                xref="paper",
                x0=0,
                x1=1,
                y0=max_val,
                y1=y_range[1],
                fillcolor="rgba(236,2,0,0.2)",
                layer="below",
                line=dict(width=0),
            )
        )

    font_family = dict(family="Montserrat, Helvetica, Arial, sans-serif")

    fig.update_layout(
        title=go.layout.Title(
            text=f"{marker.name} <br><sup>{marker.description}</sup>",
            xref="paper",
            x=0,
            font={**font_family, "size": 18}
        ),
        title_x=0.5,
        title_y=0.93,
        title_xanchor="center",
        title_yanchor="top",
        xaxis_title="Date",
        xaxis=dict(
            title_font={**font_family, "size": 14},
            tickfont={**font_family, "size": 12}
        ),
        yaxis_title=f"Value ({marker.unit})",
        yaxis=dict(
            title_font={**font_family, "size": 14},
            tickfont={**font_family, "size": 12}
        ),
        shapes=shapes,
        yaxis_range=y_range,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0.04)",
        font={**font_family, "size": 12}
    )

    pyo.plot(fig, filename=save_to, auto_open=False)
