#!/usr/bin/python3
from sys import argv
from os import mkdir, chdir, system
from shutil import copyfile
from sys import exit
from scraper import luogu_scraper, scraper
from pathlib import Path

BASE_PATH = Path('.')

problem_type = argv[1]
argv[2] = argv[2].rstrip('/')
problem = argv[2].split('/')[-1]
if 'acwing' in argv[2]:
    problem = 'acwing' + problem
a = input(f"Type = {problem_type}, Name = {problem}. Continue? [Y/n]")
if a in ['n', 'N']:
    exit(0)

try:
    mkdir(BASE_PATH / f'{problem_type}')
except FileExistsError:
    pass

try:
    mkdir(BASE_PATH / f'{problem_type}/{problem}')
except FileExistsError:
    pass

for s in ['cpp', 'in']:
    if s == 'cpp' and problem_type == 'cg':
        copyfile(
            BASE_PATH / f'template/template_{problem_type}.{s}',
            BASE_PATH / f'{problem_type}/{problem}/{problem}.{s}'
        )
    elif s == 'cpp' and problem.startswith('LightOJ'):
        copyfile(
            BASE_PATH / f'template/template_loj.{s}', 
            BASE_PATH / f'{problem_type}/{problem}/{problem}.{s}'
        )
    else:
        copyfile(
            BASE_PATH / f'template/template.{s}', 
            BASE_PATH / f'{problem_type}/{problem}/{problem}.{s}'
        )

with open(BASE_PATH / f'{problem_type}/{problem}/{problem}.cpp') as f:
    cppcode = f.read()

cppcode = cppcode.replace('freopen("", "r", stdin);', f'freopen("{problem}.in", "r", stdin);')

with open(BASE_PATH / f'{problem_type}/{problem}/{problem}.cpp', 'w') as f:
    f.write(cppcode)

problem_path = str(BASE_PATH / f'{problem_type}/{problem}/{problem}.cpp')
system('code -g ' + problem_path)

# chdir(f'./{problem_type}/{problem}/')
print("Fetching input data...")

input_value = scraper(problem.replace('acwing', ''))
with open(BASE_PATH / f'{problem_type}/{problem}/{problem}.in', 'w') as f:
    f.write(input_value)
print("Done with input data:\n---BEGIN---")
print(input_value)
print(F"---END---\nEnjoy coding {problem}!")


