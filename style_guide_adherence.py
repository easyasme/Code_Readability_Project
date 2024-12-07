import sys
import os
import re
import subprocess
from io import StringIO
from pylint.lint import Run
from pylint.reporters.text import TextReporter

def style_adherence(file):
    output = StringIO()
    reporter = TextReporter(output)

    Run(args=[file], reporter=reporter, exit=False)

    match = re.search(r"Your code has been rated at ([\d\.]+)/10", output.getvalue())

    if match:
        score = float(match.group(1))
    else:
        return -1

    return score

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            cfile = os.path.join(sys.argv[1])
            score = style_adherence(cfile)
            print(score)
        except FileNotFoundError:
            print(f"Error: The file '{sys.argv[1]}' was not found.")
        except OSError as e:
            print(f"Error: {e}")
    else:
        print("Usage: python style_guide_adherence.py <filename>")
    