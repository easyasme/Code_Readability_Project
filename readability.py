import sys
import os
import csv
import zipfile
import shutil
from os import path

import style_guide_adherence
import name_quality
import comment_ratio
import complexity

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            zfile = path.join(sys.argv[1])

            with zipfile.ZipFile(zfile, 'r') as zip_ref:
                zip_ref.extractall("temp_dest")

            data = [["#", "Style Guide Adherence", "Variable Name Quality"]]
            for root, dirs, files in os.walk("temp_dest"):
                py_files = [x for x in files if x.endswith('py')]
                for i, file in enumerate(py_files):
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        print(f"Processing file: {file_path}")

                        adherence_score = style_guide_adherence.style_adherence(file_path)
                        with open(file_path, 'r') as file:
                            content = file.read()
                            var_name_score = name_quality.calculate_quality(content)
                            #commnet_ratio = comment_ratio.get_ratio(content)
                            #complexity_score = complexity.get_complexity(content)

                        result = [i, adherence_score, var_name_score]
                        data.append(result)

            output_file = "code_readability.csv"
            with open(output_file, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerows(data)

            shutil.rmtree("temp_dest")
            
        except FileNotFoundError:
            print(f"Error: The file '{sys.argv[1]}' was not found.")
        except OSError as e:
            print(f"Error: {e}")
    else:
        print("Usage: python readability.py <filename.zip>")
