# pip install radon
from os import path
import radon.complexity
import sys

# Given the code snippet in string format, returns the cyclomatic complexity (CC)
def get_complexity(snippet):
    ccresults = radon.complexity.cc_visit(snippet)
    # Get the CC score of each function in the snippet
    complexities = [result.complexity for result in ccresults]
    # Return the average, or 0 if there are no functions
    return sum(complexities) / len(complexities) if len(complexities) else 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            cfile = path.join(sys.argv[1])
            with open(cfile, 'r') as file:
                content = file.read()
                avg_score = get_complexity(content)
                print(avg_score)
        except FileNotFoundError:
            print(f"Error: The file '{sys.argv[1]}' was not found.")
        except OSError as e:
            print(f"Error: {e}")
    else:
        print("Usage: python complexity.py <filename>")
        print("Example: python complexity.py extracted_codes/code_snippet_468.py")
