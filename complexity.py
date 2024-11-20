# pip install radon
from os import path
import radon
import radon.complexity

# Given the code snippet in string format, returns the cyclomatic complexity (CC)
def get_complexity(snippet):
    ccresults = radon.complexity.cc_visit(snippet)
    # Get the CC score of each function in the snippet
    complexities = [result.complexity for result in ccresults]
    # Return the average
    avg_score = sum(complexities) / len(complexities)
    return avg_score

if __name__ == "__main__":
    cfile = path.join("extracted_codes/code_snippet_2.py")
    with open(cfile, 'r') as file:
        content = file.read()
        avg_score = get_complexity(content)
        print(avg_score)
