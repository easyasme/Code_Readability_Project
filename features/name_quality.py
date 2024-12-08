import sys
from os import path
import re
import ast
import statistics
import keyword
from spellchecker import SpellChecker
import spacy
from itertools import combinations

def calculate_quality(snippet):
    variable_names = get_variable_names(snippet) + get_function_names(snippet)

    if len(variable_names) != 0:
        valid_names_score = calculate_valid_name_score(variable_names) # 1. Check whether it is a valid Python name
        name_lengths_score = calculate_length_score(variable_names) # 2. Check length
        valid_words_score, valid_words = calculate_spelling_score(variable_names) # 3. Check spelling
        if len(valid_words) > 1:
            avg_similarity_score = calculate_names_lexical_similarity(valid_words) # 4. Calculate pairwise similarity
        else:
            avg_similarity_score = 1
        
        return (valid_names_score + name_lengths_score + valid_words_score + avg_similarity_score)/4
   
    return 0

def get_variable_names(snippet):
    pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*='

    # Find all matches at the beginning of lines
    matches = re.findall(pattern, snippet, flags=re.MULTILINE)

    result = [item[0] for item in list(set(matches))]
    return result  # Remove duplicates

def get_function_names(snippet):
    tree = ast.parse(snippet)
    
    # Extract function names
    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    function_names = list(set(function_names))
    return function_names

def calculate_valid_name_score(variable_names):
    valid_names = [
        1 if name.isidentifier() and not keyword.iskeyword(name) else 0 
        for name in variable_names
    ]

    return statistics.fmean(valid_names)

def calculate_length_score(variable_names):
    name_lengths = [
        (1 - len(name)/15) for name in variable_names
    ]

    return statistics.fmean(name_lengths)

def calculate_spelling_score(variable_names):
    spell = SpellChecker()
    valid_words = []
    invalid_words = []
    for name in variable_names:
        split_name = []

        for word in re.split(r'[\._]+', name):
            if word:
                if not word.isupper():
                    split_name.extend(re.findall(r'[A-Z][^A-Z]*', word))
                else:
                    split_name.append(word)

        for word in split_name:
            if word in spell:
                valid_words.append(word)
            else:
                invalid_words.append(word)

    return len(valid_words)/len(variable_names), valid_words

def calculate_names_lexical_similarity(valid_words):
    nlp = spacy.load("en_core_web_md")
    processed_words = {word: nlp(word) for word in valid_words}
    similarity_scores = [
        processed_words[word1].similarity(processed_words[word2])
        for word1, word2 in combinations(valid_words, 2)
    ]
    return statistics.fmean(similarity_scores)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            cfile = path.join(sys.argv[1])
            with open(cfile, 'r') as file:
                content = file.read()
                quality_score = calculate_quality(content)
        except FileNotFoundError:
            print(f"Error: The file '{sys.argv[1]}' was not found.")
        except OSError as e:
            print(f"Error: {e}")
    else:
        print("Usage: python name_quality.py <filename>")
    