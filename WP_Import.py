import os
import json
import pandas as pd
import re
import sys

def extract_json(content):
    """Extract JSON content from a <script> tag if present."""
    match = re.search(r'<script[^>]*type="application/ld\\+json"[^>]*>(.*?)</script>', content, re.DOTALL)
    return match.group(1) if match else content

def process_json_files(input_dir, output_file):
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' is not a valid directory.")
        return

    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    if not files:
        print("No JSON files found in the specified folder.")
        return

    wp_category = input("Enter the wp_category value: ")

    data_dict = {
        "wp_title": [],
        "wp_name": [],
        "wp_category": [],
        "wp_content": []
    }

    for file in files:
        file_path = os.path.join(input_dir, file)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            json_str = extract_json(content)

            try:
                json_data = json.loads(json_str)
                name = json_data.get("name", "").strip()
                content = json.dumps(json_data, ensure_ascii=False, indent=4)
                wrapped_content = (
                    "<!-- wp:html -->\n"
                    "<script data-testid=\"page-schema\" type=\"application/ld+json\">\n"
                    f"{content}\n"
                    "</script>\n"
                    "<!-- /wp:html -->"
                )

                data_dict["wp_title"].append(name)
                data_dict["wp_name"].append(name)
                data_dict["wp_category"].append(wp_category)
                data_dict["wp_content"].append(wrapped_content)

            except json.JSONDecodeError:
                print(f"Error reading {file}: Invalid JSON format.")

    df = pd.DataFrame(data_dict)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")  # Use utf-8-sig for Excel-friendly CSVs
    print(f"CSV saved as {output_file}")

if __name__ == "__main__":
    input_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.csv"

    process_json_files(input_dir, output_file)
