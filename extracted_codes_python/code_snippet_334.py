#!/usr/bin/env python

from shpy import *
from itertools import product
from subprocess import list2cmdline, call


def do_st():
    if(len(c("git config g.autofetch", exit=True))):
        c("git fetch")
    upstream = "".join(c("git rev-parse --abbrev-ref --symbolic-full-name '@{{u}}'", exit=True))
    #branches = ["master", "a", "b", "c"]
    branches = ["HEAD", upstream]
    branchstring = " ".join(branches)
    commits = c("git rev-parse {}", branchstring)
    boundaries = []
    contexts = [c("git rev-list --first-parent --max-count 3 {}", commit) for commit in commits]
    allcontexts = sum(map(lambda x: x[:-1], contexts), [])

    for context in contexts:
        bound = context[-1]
        if not bound in allcontexts:
            boundaries.append(bound)
    p(c("git --no-pager log --color --graph --boundary --format=format:\"%C(red)%h%C(reset) %C(yellow)%ad%C(reset) %s %C(green)[%an]%C(auto)%d%C(reset)\" --abbrev-commit --date=relative {} {}", " ".join(commits), " ".join(map(lambda x: "^" + x, boundaries)), q=True))
    p(c("git stash list --format=format:\"S %C(red)%gd%C(reset) %C(yellow)%cr%C(reset) %s \""))
    ignored = []
    untracked = []
    statused = []
    for line in c("git -c color.ui=always status -sbuall --ignored"):
        if line.startswith("[31m!!"):
            ignored.append(line)
        elif line.startswith("[31m??"):
            untracked.append(line)
        else:
            statused.append(line)

    if len(ignored) > 10:
        p("X: {}", len(ignored))
    else:
        p(ignored)

    if len(untracked) > 10:
        p("U: {}", len(untracked))
    else:
        p(untracked)

    p(reversed(statused))

    username = "".join(c("git config --local user.name", exit=True))
    email = "".join(c("git config --local user.email", exit=True))
    if username == "" or email == "":
        p("[38;5;202mWARNING: user info not set in repo: git config user.name ''; git config user.email ''[0m")

def do_branch():
    do_st()
    p(c("git -c color.ui=always  branch -vvv"))

def do_stash():
    ignored = 0
    untracked = 0
    modified = 0
    indexed = 0
    for line in c("git -c color.ui=always status -sbuall --ignored"):
        if line.startswith("[32m"):
            indexed += 1
        elif line.startswith("[31m!!"):
            ignored += 1
        elif line.startswith("[31m??"):
            untracked += 1
        elif line.startswith(" [31m"):
            modified +=1

    c("git stash save --all \"A: {} M: {} U: {} I: {}\"", indexed, modified, untracked, ignored)
    do_st()

def do_pop():
    c("git stash pop --index")
    do_st()

parser.add_argument("gitcommand", nargs=argparse.REMAINDER, type=str)

a = init()

myargs = {
    'branch': do_branch,
    'stash' : do_stash,
    'pop' : do_pop
}

if(len(a.gitcommand) == 0):
    do_st()
elif a.gitcommand[0] in myargs and len(a.gitcommand) == 1:
    myargs[a.gitcommand[0]]()
else:
    call(["git"] + a.gitcommand)
    do_st()
