#! /usr/bin/env python3

#===== imports =====#
import argparse
import copy
import datetime
import glob
import os
import re
import shutil
import subprocess
import sys

#===== args =====#
parser = argparse.ArgumentParser()
parser.add_argument('--run', '-r', action='store_true')
parser.add_argument('--deploy', '-d', action='store_true')
parser.add_argument('--lint-all', '-l', action='store_true')
parser.add_argument('--lint-vue', action='store_true')
parser.add_argument('--lint-scss', action='store_true')
parser.add_argument('--lint-fix', '--lf', action='store_true')
parser.add_argument('--deploy-staging', '--ds', action='store_true')
parser.add_argument('--deploy-prod', '--dp', action='store_true')

args = parser.parse_args()

#===== consts =====#
DIR = os.path.dirname(os.path.realpath(__file__))

#===== setup =====#
os.chdir(DIR)

#===== helpers =====#
def blue(text):
    return '\x1b[34m' + text + '\x1b[0m'

def timestamp():
    return '{:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.datetime.now())

def invoke(
    *args,
    popen=False,
    no_split=False,
    stdout=False,
    quiet=False,
    **kwargs,
):
    if len(args) == 1 and not no_split:
        args = args[0].split()
    if not quiet:
        print(blue('-'*40))
        print(timestamp())
        print(os.getcwd()+'$', end=' ')
        for i, v in enumerate(args):
            if re.search(r'\s', v):
                v = v.replace("'", """ '"'"' """.strip())
                v = f"'{v}'"
            if i != len(args)-1:
                end = ' '
            else:
                end = ';\n'
            print(v, end=end)
        if kwargs: print(kwargs)
        if popen: print('popen')
        print()
    if kwargs.get('env') != None:
        env = copy.copy(os.environ)
        env.update(kwargs['env'])
        kwargs['env'] = env
    if popen:
        return subprocess.Popen(args, **kwargs)
    else:
        if 'check' not in kwargs: kwargs['check'] = True
        if stdout: kwargs['capture_output'] = True
        result = subprocess.run(args, **kwargs)
        if stdout:
            result = result.stdout.decode('utf-8').strip()
        return result

def git_state():
    diff = invoke('git diff', stdout=True)
    diff_cached = invoke('git diff --cached', stdout=True)
    with open('git-state', 'w') as git_state:
        git_state.write(invoke('git show --name-only', stdout=True)+'\n')
        if diff:
            git_state.write('\n===== diff =====\n')
            git_state.write(diff+'\n')
        if diff_cached:
            git_state.write('\n===== diff --cached =====\n')
            git_state.write(diff_cached+'\n')


#===== main =====#
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

if args.run:
    invoke(f'npm run dev')

if args.deploy:
    invoke(f'npm run build')

if args.lint_all:
    invoke('npm run lint-vue')
    invoke('npm run lint-scss')

if args.lint_vue:
    invoke('npm run lint-vue')

if args.lint_scss:
    invoke('npm run lint-scss')

if args.lint_fix:
    invoke('npm run lint-fix')

if args.deploy_staging:
    shutil.rmtree('dist', ignore_errors=True)
    invoke('npm run build', env={'NODE_ENV': 'staging'})
    for i in glob.glob('dist/*'):
        invoke(f'scp -r {i} root@staging.bloomo.app:/root/bloomo/static')
    git_state()
    invoke(f'scp git-state root@staging.bloomo.app:/root/bloomo/frontend-git-state')

if args.deploy_prod:
    shutil.rmtree('dist', ignore_errors=True)
    invoke('npm run build', env={'NODE_ENV': 'production'})
    for i in glob.glob('dist/*'):
        invoke(f'scp -r {i} root@bloomo.app:/root/bloomo/static')
    git_state()
    invoke(f'scp git-state root@bloomo.app:/root/bloomo/frontend-git-state')
