#!/usr/bin/env python3

# filename: load_wellnessfx.py
# Script to extract WellnessFX data and generate an interactive dashboard

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

import os
import pandas as pd
import sys
import biomarkerdash.utils as util
import biomarkerdash.plotting as plot
import biomarkerdash.html as htm
import biomarkerdash.biomarker as bm
from typing import List, Dict, Optional, Tuple


import yaml


def load_categories(filename: str) -> Dict:
    """Load biomarker categories from a YAML file."""
    with open(filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 load_wellnessfx.py path_to_csv_file")
        sys.exit(1)

    csv_path: str = sys.argv[1]
    biomarkers = util.load_wellnessfx_biomarkers(csv_path)

    plot_output_dir = "_includes"
    category_page_output_dir = "_categories"
    os.makedirs(plot_output_dir, exist_ok=True)
    os.makedirs(category_page_output_dir, exist_ok=True)
    categories = load_categories("categories.yaml")

    output_files = []

    for category, subcategories in categories.items():
        html_content = []
        html_content.append(f'<h2 id="{category}">{category}</h2>')

        for subcategory, biomarkers_list in subcategories.items():
            html_content.append(f'<h3 id="{subcategory}">{subcategory}</h3>')

            # Generate plots for biomarkers in the subcategory
            for marker_name in biomarkers_list:
                marker_obj = biomarkers.get(marker_name)
                if marker_obj:  # Check if biomarker data exists
                    filename = os.path.join(
                        plot_output_dir, util.generate_filename(marker_name)
                    )

                    # Save the individual plot
                    plot.plot_history(marker_obj, save_to=filename)
                    print(f"Plot for {marker_name} saved to {filename}.")

                    # Read the generated HTML file and store its content
                    if not os.path.exists(filename):
                        print(f"{filename} not found, skipping")
                        continue
                    with open(filename, "r", encoding="utf-8") as f:
                        html_content.append(f.read())

        output_file = htm.combine_html_files(category, html_content)
        output_files.append(output_file)

    # Now that all category files have been generated, create the TOC
    header = htm.create_header_toc(
        {cat: util.generate_filename(cat) for cat in categories.keys()}
    )

    # Prepend TOC to each category file
    for output_file in output_files:
        with open(output_file, "r+", encoding="utf-8") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(header + content)

    index_page_filename = "BiomarkerDashboard.html"
    index_page_html_content = htm.create_header_toc(
        {
            cat: os.path.join(
                category_page_output_dir, util.generate_filename(cat)
            )
            for cat in categories.keys()
        }
    )

    index_page_html_content += "</body></html>"

    with open(index_page_filename, "w", encoding="utf-8") as f:
        f.write(index_page_html_content)

    print("Generated BiomarkerDashboard.html")
