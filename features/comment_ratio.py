# pip install radon
from os import path
import radon.raw
import sys

def get_ratio(snippet):
    data = radon.raw.analyze(snippet)
    return data.comments / data.sloc

def classify_ratio(ratio):
    """
    - Good: 15% <= ratio < 30%
    - Medium: 0% <= ratio < 15% or 30% <= ratio < 40%
    - Bad: 40% <= ratio < 60%
    - Very Bad: ratio >= 60%
    """
    if 0.15 <= ratio < 0.30:
        return "Good"
    elif 0 <= ratio < 0.15 or 0.30 <= ratio < 0.4:
        return "Medium"
    elif 0.4 <= ratio < 0.6:
        return "Bad"
    elif ratio >= 0.6:
        return "Very Bad"
    else:
        return "Unknown"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            cfile = path.join(sys.argv[1])
            with open(cfile, 'r') as file:
                content = file.read()
                ratio = get_ratio(content)
                classification = classify_ratio(ratio)
                print(f"Classification: {classification}")
        except FileNotFoundError:
            print(f"Error: The file '{sys.argv[1]}' was not found.")
        except OSError as e:
            print(f"Error: {e}")
    else:
        print("Usage: python comment_ratio.py <filename>")
        print("Example: python comment_ratio.py extracted_codes/code_snippet_468.py")