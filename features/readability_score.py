import os
import re
import sys


# Given the path to the Python file, returns a simple readability score
def get_readability(filepath: str):
    with open(filepath, 'r') as file:
        code = file.readlines()

    if not code:
        print(f"Error: The file '{filepath}' is empty.")
        return None

    # Metrics to compute readability
    total_lines = len(code)
    comment_lines = 0
    blank_lines = 0
    long_lines = 0
    total_line_length = 0
    poorly_named_variables = 0
    total_variables = 0

    # Define a regex for poorly named variables (e.g., single letters, no underscores)
    poorly_named_regex = r'^\s*[a-zA-Z]\s*$'

    # Analyze the code line by line
    for line in code:
        stripped = line.strip()

        # Count comments
        if stripped.startswith("#"):
            comment_lines += 1

        # Count blank lines
        if not stripped:
            blank_lines += 1

        # Count long lines
        if len(line) > 80:
            long_lines += 1

        # Measure line lengths
        total_line_length += len(line)

        # Analyze variable names (simple heuristic: look for assignment statements)
        match = re.match(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line)
        if match:
            total_variables += 1
            if re.match(poorly_named_regex, match.group(1)):
                poorly_named_variables += 1

    # Compute scores
    avg_line_length = total_line_length / total_lines
    comment_ratio = comment_lines / total_lines
    blank_line_ratio = blank_lines / total_lines
    long_line_ratio = long_lines / total_lines
    poorly_named_ratio = poorly_named_variables / total_variables if total_variables else 0

    # Readability score (heuristic-based formula, lower is better)
    readability_score = (
            (1 - comment_ratio) * 20 +  # Encourage more comments
            blank_line_ratio * 10 +  # Encourage spacing for readability
            long_line_ratio * 30 +  # Penalize long lines
            poorly_named_ratio * 40 +  # Penalize poor variable names
            avg_line_length / 80 * 20  # Penalize high average line length
    )

    return round(readability_score, 2)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if os.path.exists(sys.argv[1]):
            readability = get_readability(sys.argv[1])
            print(f"{readability}")
        else:
            print(f"Error: The file '{sys.argv[1]}' was not found.")
    else:
        print("Usage: python readability.py <filename>")
        print("Example: python readability.py extracted_codes/code_snippet_468.py")
