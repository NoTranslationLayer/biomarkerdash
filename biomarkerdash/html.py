import os
import biomarkerdash.utils as util
from typing import List, Dict, Optional, Tuple


def combine_html_files(
    category: str, plot_html_list: List[str], output_directory: str = "_categories") -> str:
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
    combined_html += "</body></html>"

    sanitized_filename = util.generate_filename(category)
    output_path = os.path.join(output_directory, sanitized_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(combined_html)

    print(f"Wrote {category} page to {output_path}")
    return output_path


def load_css(css_filepath: str) -> str:
    with open(css_filepath, 'r', encoding='utf-8') as f:
        return f.read()

def create_header_toc(category_files: Dict[str, str], css_filepath: str = "_includes/styles.css"):
    """
    Create a header and table of contents HTML linking to various category pages.

    Args:
    - category_files (Dict[str, str]): Dictionary mapping category names to their file names.
    - css_filepath (str): Path to the CSS file.
    """

    css_content = load_css(css_filepath)

    # Header
    header_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <style>
    """
    header_html += css_content
    header_html += """
        </style>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Combined Plots</title>
    </head>
    <body>
    """
    header_html += "<h1>Biomarker Dashboard</h1><ul>"

    for category, filename in category_files.items():
        header_html += f'<li><a href="{filename}">{category}</a></li>'

    header_html += "</ul><hr>"

    return header_html
