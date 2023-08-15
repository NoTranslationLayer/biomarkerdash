#!/usr/bin/env python3

import os
import pandas as pd
import sys
import biomarkerdash.utils as util
import biomarkerdash.plotting as plot
import biomarkerdash.biomarker as bm
from typing import List, Dict, Optional, Tuple


import yaml

def load_categories(filename: str) -> Dict:
    """Load biomarker categories from a YAML file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def combine_html_files(plot_html_list: List[str], output_file: str):
    """
    Combine multiple HTML files into a single page.

    Args:
    - plot_html_list (List[str]): List of HTML contents to combine.
    - output_file (str): Name of the combined output file.
    """
    # Header
    combined_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <style>
            body {
                font-family: "proxima-nova-soft", "proxima-nova", Helvetica, Arial, sans-serif;
                font-weight: 500;
                line-height: 1.2;
                color: #555;
            }
            
            h2 {
                border-bottom: 1px solid lightgrey;
                padding-bottom: 10px;
            }
        </style>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Combined Plots</title>
    </head>
    <body>
    """
    for plot_html in plot_html_list:
        combined_html += plot_html

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


    categories = load_categories('categories.yaml')

    html_content = []

    for category, subcategories in categories.items():
        html_content.append(f"<h2>{category}</h2>")
        
        for subcategory, biomarkers_list in subcategories.items():
            html_content.append(f"<h3>{subcategory}</h3>")

            # Generate plots for biomarkers in the subcategory
            for marker_name in biomarkers_list:
                marker_obj = biomarkers.get(marker_name)
                if marker_obj:  # Check if biomarker data exists
                    filename = os.path.join(plot_output_dir, util.generate_filename(marker_name))
                    
                    # Save the individual plot
                    plot.plot_history(marker_obj, save_to=filename)
                    print(f"Plot for {marker_name} saved to {filename}.")

                    # Read the generated HTML file and store its content
                    if not os.path.exists(filename):
                        print(f"{filename} not found, skipping")
                        continue
                    with open(filename, 'r', encoding='utf-8') as f:
                        html_content.append(f.read())

    combine_html_files(html_content, "dashboard.html")
    print("All plots combined into dashboard.html.")
