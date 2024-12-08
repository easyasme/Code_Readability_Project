#!/usr/bin/env python3

import os
import pyperclip
import re
import sys
from shutil import copyfile
#from Crypto.Cipher import AES
import base64

#
# this script should ...
#
# vl -i ... interactive mode
#
#
args       = sys.argv
vault_file = os.path.expanduser("~/.vl")
actions    = list(filter(lambda x: x in ['-i', '-e'], args))

def remove_comments(lines):
    pattern = re.compile("^\s*--") 
    return list(filter(lambda x: not pattern.match(x) and x != '', lines))

def read_file(file):
    f = open(vault_file, 'r') 
    lines = f.read().split('\n')
    f.close() 
    return remove_comments(lines)

def remove_blank(xs):
    return list(filter(lambda x: x != '', xs))

def parse_lines(lines):
    return list(map(lambda x: remove_blank(x.split(' ')), lines))

def ask(lines):
    res = input('> ')
    if(re.compile("^\d+$").match(res)):
        target = lines[int(res)]
        pyperclip.copy(target[2])
        print('password copied to the clipboard!')
    else:
        ask(lines)

def encode(vault_file, secret_key):
    print('encoded')
    # copyfile(vault_file, vault_file + '.bk')
    # cipher  = crypto.AES.new(secret_key, AES.MODE_ECB)
    # encoded = base64.b64encode(cipher.encrypt(read_file(vault_file)))
    # print(encoded)

if('-e' in actions):
    secret_key = os.path.expanduser('~/.ssh/id_rsa')
    encode(vault_file, secret_key)
elif('-i' in actions):
    # interactive mode
    lines = read_file(vault_file)
    print('')
    lines = parse_lines(lines)
    for i, (key, email, pwd) in enumerate(lines):
        print(f"[{i}] {key}")
    print('')
    ask(lines)
