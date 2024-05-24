# Filter the ones that are bad
# 202403010927_html 4790 -> 4520
# 202403080504_html 11971 -> 11084
# 202403080515_html 21385 -> 19751

import os
import glob
from bs4 import BeautifulSoup

# Define paths to HTML and JSON directories
html_path = '/home/dxleec/gysun/datasets/estate/202403080504_html'
json_path = '/home/dxleec/gysun/datasets/estate/202403080504_json'

# Retrieve all HTML files
html_files = glob.glob(os.path.join(html_path, '*.html'))

# Function to find the matching JSON file given an HTML file name
def get_matching_json(html_file_name):
    base_name = os.path.splitext(os.path.basename(html_file_name))[0]
    json_file_name = os.path.join(json_path, f'{base_name}.json')
    return json_file_name if os.path.exists(json_file_name) else None

# Process each HTML file
for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Check if the HTML file should be deleted
    if soup.title is None or '404' in str(soup.title) or '403' in str(soup.title):
        # Find the corresponding JSON file
        json_file = get_matching_json(html_file)

        # Delete the HTML file
        os.remove(html_file)
        print(f'Deleted HTML file: {html_file}')

        # If the JSON file exists, delete it
        if json_file:
            os.remove(json_file)
            print(f'Deleted JSON file: {json_file}')
