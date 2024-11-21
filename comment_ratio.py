# pip install radon
from os import path
import radon.raw
import sys

def get_ratio(snippet):
    data = radon.raw.analyze(snippet)
    return data.comments / data.sloc

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            cfile = path.join(sys.argv[1])
            with open(cfile, 'r') as file:
                content = file.read()
                ratio = get_ratio(content)
                print(ratio) # ratio is numbers of lines of comment / numbers of lines of code
        except FileNotFoundError:
            print(f"Error: The file '{sys.argv[1]}' was not found.")
        except OSError as e:
            print(f"Error: {e}")
    else:
        print("Usage: python complexity.py <filename>")
        print("Example: python complexity.py extracted_codes/code_snippet_468.py")
