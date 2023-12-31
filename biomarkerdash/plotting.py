# filename: plotting.py
# Utilities to plot biomarker time series data

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

import numpy as np
import plotly.graph_objects as go
import plotly.offline as pyo
from typing import Optional, Tuple

import biomarkerdash.biomarker as bm

from biomarkerdash.constants import (
    COLOR_RED,
    COLOR_GREEN,
    COLOR_LINE,
    COLOR_BG_OUTSIDE_REF_RANGE,
)


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
    if min_val is not None and max_val is not None:
        return COLOR_GREEN if min_val <= value <= max_val else COLOR_RED
    elif min_val is not None:
        return COLOR_GREEN if value >= min_val else COLOR_RED
    elif max_val is not None:
        return COLOR_GREEN if value <= max_val else COLOR_RED
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
            line=dict(color=COLOR_LINE),
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
                fillcolor=COLOR_BG_OUTSIDE_REF_RANGE,
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
                fillcolor=COLOR_BG_OUTSIDE_REF_RANGE,
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
            font={**font_family, "size": 18},
        ),
        title_x=0.5,
        title_y=0.93,
        title_xanchor="center",
        title_yanchor="top",
        xaxis_title="Date",
        xaxis=dict(
            title_font={**font_family, "size": 14},
            tickfont={**font_family, "size": 12},
        ),
        yaxis_title=f"Value ({marker.unit})",
        yaxis=dict(
            title_font={**font_family, "size": 14},
            tickfont={**font_family, "size": 12},
        ),
        shapes=shapes,
        yaxis_range=y_range,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0.04)",
        font={**font_family, "size": 12},
    )

    pyo.plot(fig, filename=save_to, auto_open=False)
