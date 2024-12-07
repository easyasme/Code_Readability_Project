import sys
import os
import re
import csv
import zipfile
import shutil
import subprocess

import style_guide_adherence
import name_quality
import comment_ratio
import complexity
import maxlinesfeature
import readability_score

def check_py2(file):
    try:
        # Run 2to3 command with the -l option to list Python 2 syntax
        result = subprocess.run(
            ["2to3", "-l", file],
            capture_output=True,  # Capture the output
            text=True  # Ensure the output is returned as a string
        )
        
        # Check if the command was successful
        if result.returncode == 0:
            filename = os.path.basename(file)
            subprocess.run(
                ["2to3", file, "-n", "-W", "-o", "converted_files"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            converted_filepath= os.path.join("converted_files", filename)
            return converted_filepath
        else:
            return file
    except FileNotFoundError:
        print("The `2to3` tool is not installed or not in your PATH.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            zfile = os.path.join(sys.argv[1])

            with zipfile.ZipFile(zfile, 'r') as zip_ref:
                zip_ref.extractall("temp_dest")

            data = [["#", "Style Guide Adherence", "Variable Name Quality", "Complexity Score", "Max Line", "Comment Ratio", "Readability"]]
            for root, dirs, files in os.walk("temp_dest"):
                py_files = [x for x in files if x.endswith('py')]
                for file in py_files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        file_path = check_py2(file_path)

                        print(f"Processing file: {file_path}")

                        match = re.search(r'\d+', file_path)
                        id = int(match.group())

                        try:
                            adherence_score = '?' if style_guide_adherence.style_adherence(file_path) < 0 else style_guide_adherence.style_adherence(file_path)
                            complexity_score = complexity.get_complexity(file_path) or '?'
                            max_line = maxlinesfeature.max_lines(file_path)
                            readability = readability_score.get_readability(file_path)
                            with open(file_path, 'r') as file:
                                content = file.read()
                                var_name_score = name_quality.calculate_quality(content)
                                commnet_ratio = comment_ratio.get_ratio(content)

                            result = [id, adherence_score, var_name_score, complexity_score, max_line, commnet_ratio, readability]
                            data.append(result)
                        except Exception as e:
                            print(f"Error processing file {file_path}: {e}")
                            continue
            output_file = "code_readability2.csv"
            with open(output_file, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerows(data)

            shutil.rmtree("temp_dest")
            shutil.rmtree("converted_files")
            
        except FileNotFoundError:
            print(f"Error: The file '{sys.argv[1]}' was not found.")
        except OSError as e:
            print(f"Error: {e}")
        except SyntaxError:
            print(f"Error: The file '{sys.argv[1]}' has syntax error.")
    else:
        print("Usage: python readability.py <filename.zip>")
