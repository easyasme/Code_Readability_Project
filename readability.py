import sys
import os
import re
import csv
import zipfile
import shutil

import style_guide_adherence
import name_quality
import comment_ratio
import complexity
import maxlinesfeature
import readability_score

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

                        print(f"Processing file: {file_path}")

                        match = re.search(r'\d+', file_path)
                        id = int(match.group())

                        try:
                            adherence_score = style_guide_adherence.style_adherence(file_path)
                            adherence_score = '?' if adherence_score < 0 else adherence_score
                            complexity_score = complexity.get_complexity(file_path)
                            complexity_score = '?' if complexity_score == None else complexity_score
                            max_line = maxlinesfeature.max_lines(file_path)
                            readability = readability_score.get_readability(file_path)
                            with open(file_path, 'r') as file:
                                content = file.read()
                                var_name_score = name_quality.calculate_quality(content)
                                ratio = comment_ratio.classify_ratio(comment_ratio.get_ratio(content))

                            result = [id, adherence_score, var_name_score, complexity_score, max_line, ratio, readability]
                            data.append(result)
                        except Exception as e:
                            print(f"Error processing file {file_path}: {e}")
                            continue
            output_file = "csv/code_pypi_readability.csv"
            with open(output_file, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerows(data)

            shutil.rmtree("temp_dest")
            shutil.rmtree("converted_files")
            shutil.rmtree("complexity_temp")
            
        except FileNotFoundError:
            print(f"Error: The file '{sys.argv[1]}' was not found.")
        except OSError as e:
            print(f"Error: {e}")
        except SyntaxError:
            print(f"Error: The file '{sys.argv[1]}' has syntax error.")
    else:
        print("Usage: python readability.py <filename.zip>")
