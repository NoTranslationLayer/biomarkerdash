#!/usr/bin/env python3

import os
import pandas as pd
import sys
import biomarkerdash.utils as util
import biomarkerdash.plotting as plot
import biomarkerdash.biomarker as bm
from typing import List, Dict, Optional, Tuple


def combine_html_files(filenames: List[str], output_file: str):
    """
    Combine multiple HTML files into a single page.

    Args:
    - filenames (List[str]): List of filenames to combine.
    - output_file (str): Name of the combined output file.
    """
    # Header
    combined_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Combined Plots</title>
    </head>
    <body>
    """

    # Embed each file's content
    for filename in filenames:
        if not os.path.exists(filename):
            print(f"{filename} not found, skipping")
            continue
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            start_index = content.find('<body>') + len('<body>')
            end_index = content.find('</body>')
            combined_html += content[start_index:end_index]

    # Footer
    combined_html += "</body></html>"

    # Write combined content to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_html)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 load_wellnessfx.py path_to_csv_file")
        sys.exit(1)

    csv_path: str = sys.argv[1]
    biomarkers = util.load_wellnessfx_biomarkers(csv_path)

    plot_output_dir = "_includes"
    os.makedirs(plot_output_dir, exist_ok=True)

    html_files = []
    for marker_name, marker_obj in biomarkers.items():
        filename = os.path.join(plot_output_dir, util.generate_filename(marker_name))
        html_files.append(filename)
        plot.plot_history(marker_obj, save_to=filename)
        print(f"Plot for {marker_name} saved to {filename}.")

    combine_html_files(html_files, "dashboard.html")
    print("All plots combined into dashboard.html.")