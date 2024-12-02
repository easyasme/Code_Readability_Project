# pip install radon
# pip install 2to3
import os
import radon.complexity
import sys
import subprocess

# Given the path to the code snippet in string format, returns the cyclomatic complexity (CC)
def get_complexity(filepath: str):
	snippet = None
	with open(filepath, 'r') as file:
		snippet = file.read()
		
	temp_dir = "complexity_temp"
	if not os.path.exists(temp_dir):
		os.mkdir(temp_dir)
	
	ccresults = None
	try:
		ccresults = radon.complexity.cc_visit(snippet)
	except SyntaxError as e:
		filename = os.path.basename(filepath)
		# print(f"SyntaxError in {filename}: {e}")
		try:
			# Syntax error in the code snippet. It might be python2 code, so we try to convert it to python3
			subprocess.run(["2to3", filepath, "-n", "-W", "-o", temp_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
			converted_filepath= os.path.join(temp_dir, filename)
			with open(converted_filepath, 'r') as file:
				snippet = file.read()
			os.remove(converted_filepath)
			ccresults = radon.complexity.cc_visit(snippet)
		except:
			# Could not convert to python3, or it was simply invalid python code.
			print(f"Error: Could not parse the code snippet in '{filepath}'")
			return None
	finally:
		if os.path.exists(temp_dir):
			for file in os.listdir(temp_dir):
				os.remove(os.path.join(temp_dir, file))
			os.rmdir(temp_dir)

	# Get the CC score of each function in the snippet
	complexities = [result.complexity for result in ccresults]
	# Return the average, or 0 if there are no functions
	return sum(complexities) / len(complexities) if len(complexities) else 0

if __name__ == "__main__":
	if len(sys.argv) > 1:
		if os.path.exists(sys.argv[1]):
			avg_score = get_complexity(sys.argv[1])
			print(avg_score)
		else:
			print(f"Error: The file '{sys.argv[1]}' was not found.")
	else:
		print("Usage: python complexity.py <filename>")
		print("Example: python complexity.py extracted_codes/code_snippet_468.py")
