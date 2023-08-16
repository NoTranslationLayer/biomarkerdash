# filename: html.py
# Utilities to generate biomarker dashboard HTML

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
import biomarkerdash.utils as util
from biomarkerdash.constants import FOOTER_HTML
from typing import List, Dict, Optional, Tuple


def combine_html_files(
    category: str,
    plot_html_list: List[str],
    output_directory: str = "_categories",
) -> str:
    """
    Combine multiple HTML sections related to a category into a single page.

    Args:
    - category (str): Name of the biomarker category.
    - plot_html_list (List[str]): List of HTML contents to combine.
    - output_directory (str): Directory to save the output file.

    Returns:
    - str: Name of the output file.
    """

    combined_html = ""

    for plot_html in plot_html_list:
        combined_html += plot_html

    # Footer
    combined_html += FOOTER_HTML

    sanitized_filename = util.generate_filename(category)
    output_path = os.path.join(output_directory, sanitized_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(combined_html)

    print(f"Wrote {category} page to {output_path}")
    return output_path


def load_css(filepath: str) -> str:
    """Load CSS content from a file."""
    with open(filepath, "r") as f:
        return f.read()


def create_header_toc(
    category_files: Dict[str, str], css_filepath: str = "_includes/styles.css"
) -> str:
    """
    Generate an HTML header and table of contents with links to category pages.

    Args:
        category_files (Dict[str, str]): A mapping of category names to their
        corresponding file names.
        css_filepath (str, optional): The file path to the desired CSS
        stylesheet. Defaults to "_includes/styles.css".

    Returns:
        str: HTML content with headers and table of contents.
    """
    css_content = load_css(css_filepath)

    # Header
    header_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
        <style>
    """
    header_html += css_content
    header_html += """
        </style>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Biomarker Dashboard</title>
    </head>
    <body>
    """
    header_html += "<h1>Biomarker Dashboard</h1><ul>"

    for category, filename in category_files.items():
        header_html += f'<li><a href="{filename}">{category}</a></li>'

    header_html += "</ul><hr>"

    return header_html
