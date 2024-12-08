#!/usr/bin/python
#
# BeetRoot -- utility for getting root via SSH
#
#
#    Copyright (C) 2014 Viktor Radnai
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import sys
import time
import re
import getpass
import pexpect
# Use tweaked version of PxSSH to get around a password expiry reminder in the
# server's login banner being erroneously interpreted as a login failure
sys.path.insert(1, os.path.abspath(os.path.dirname(__file__)))
import pxssh

usage = """
BeetRoot -- utility for getting root via SSH
======================================

Usage:
------

To run command on host:
    beetroot <host> <command>

To get a root shell on host:
    beetroot <host>

To run command on multiple hosts:
    beetroot <hostfile> <command>

If the first parameter is a valid file, it is read to obtain a list of hosts,
one per line.

Credentials file:
-----------------

The credentials are read from ~/.ssh/beetroot.creds

This must be a whitespace delimited text file. The fields are:
    1. Username
    2. Password or * to prompt
    3. Type, can be login, su or sudo or any combination separated by commas
    4. Regexp matching the hostnames this credential will be used for
"""

# Location of credentials
credfile = "/home/" + os.getlogin() + "/.ssh/beetroot.creds"
# Expect the root prompt to either contain a hash mark or the string 'root'
rootprompt = "(\[?[@\w. :/\-~]*\]?#)|(\[?root@?[\w. :/\-~]?[\$>])\s?"

# Set this to override the built-in user prompt detection
# userprompt = "(\[?[@\w. :/\-~]*\]?[\$>])\s"

# Set this to force a custom prompt in interactive mode
# customprompt = '[\u@\h \W]\$ ' # Redhat style
customprompt = '\u@\h:\w\$ '   # Debian style

passwordprompt = 'ssword'
# Debug settings:
# - 0: minimal output
# - 1: verbose mode
# - 2: debug mode, prints everything including passwords
debug = 0


def get_host():
    if len(sys.argv) < 2:
        print usage
        exit(1)

    host = sys.argv[1]
    if(not os.path.exists(host)):
        return [host]

    try:
        fd = open(host, "r")
        host = fd.readlines()
        return host

    except IOError, e:
        print "BEETROOT: ERROR: Could not open file " + host + ":"
        print e.str
        exit(2)


def get_creds(host, role):

    creds = []
    for cred in credstore:
        if re.search(role, cred[2]) != None and re.match(cred[3], host):
            if cred[1] == '*':
                prompt = "BEETROOT: Enter password for user " + cred[0] + ": "
                cred[1] = getpass.getpass(prompt)
            creds.append(cred)

    return creds

def send_password(ssh, password):
    if debug < 2:
        ssh.sendline(password)
        return
    ssh.logfile = None
    ssh.sendline(password)
    print "Sent password"
    ssh.logfile = sys.stdout

def get_windowsize():
    # This is a massive hack but so are all the alternatives below Python 3.3
    fd = os.popen("bash -ic 'echo $COLUMNS $LINES'", 'r')
    buf = fd.readline()
    arr = buf.split()
    return int(arr[0]), int(arr[1])

def do_su(ssh, password, debug = False):

    ssh.sendline('su')
    if ssh.expect(['ssword', rootprompt]):
        return True
    send_password(ssh, password)

    if ssh.expect([passwordprompt, rootprompt]) == 0:
        print "BEETROOT: ERROR: su failed"
        return False

    return True


def do_sudo(ssh, password, debug = False):

    ssh.sendline('sudo su')
    if ssh.expect([passwordprompt, "usual lecture", rootprompt]) < 2:

        send_password(ssh, password)

        if ssh.expect([passwordprompt, rootprompt]) == 0:
            print "BEETROOT: ERROR: sudo failed"
            ssh.sendcontrol('c')
            return False

    return True


def do_command(ssh, command):
    ssh.setwinsize(height, width)
    if debug: print "BEETROOT: Running command: " + command
    ssh.sendline(command)
    ssh.expect(command + '\r\n')
    while True:
        seen = ssh.expect([rootprompt, '(.+)\r\n'], timeout=86400)

        if seen == 0:
            ssh.sendline('exit')
            ssh.sendline('exit')
            break
        else:
            # Send command output to stdout
            print(ssh.match.group(1))


def do_shell(ssh):
    # set window size and custom prompt if desired
    ssh.setwinsize(height, width)
    if 'customprompt' in globals():
        ssh.sendline('PS1=\'' + customprompt + '\'')
        ssh.expect('PS1=.*\n') # read back
        ssh.expect(rootprompt)

    print "BEETROOT: Entering interactive mode, press ctrl-] to exit"
    print ssh.before.split('\n')[-1] + ssh.match.group(0), # force prompt
    ssh.logfile = None # turn off debugging
    ssh.interact()

    ssh.sendline('exit')
    ssh.sendline('exit')
    print ""


def do_login(host, user, password):

    try:
        ssh = pxssh.pxssh()
        if debug > 1: ssh.logfile = sys.stdout
        if 'userprompt' in globals():
            ssh.login(host, user, password, original_prompt = userprompt,
                auto_prompt_reset = False)
        else: ssh.login(host, user, password)
        return ssh
    except pxssh.ExceptionPxssh, e:
        if debug: print "BEETROOT: Login failed: " + str(e)
        return False


def do_logout(ssh):
    ssh.logout()
    ssh.close()



#
# main
#

# Everything after the first argument is part of the command
command = ' '.join(sys.argv[2::])

# Force the size of the expect window to be the size of our terminal
width, height = get_windowsize()

# Global credential store variable
credstore = []

try:
    fd = open(credfile, "r")
    for line in fd.readlines():
        if line == '' or line[0] == '#': continue
        credstore.append(line.split())
except IOError, e:
    print "BEETROOT: ERROR: Could not get credentials"
    exit(3)


for host in get_host():
    # ignore comments and blanks, strip newlines
    if host == '' or host[0] == '#': continue
    host = host.strip()

    try:
        ssh = False
        cred = []
        for cred in get_creds(host, "login"):
            print "BEETROOT: Login to " + host + " with user " + cred[0]
            ssh = do_login(host, cred[0], cred[1])
            if ssh: break

        if not ssh:
            print "BEETROOT: ERROR: No credentials to log into host " + host
            continue

        status = False
        if re.search(rootprompt, ssh.before) != None:
            ssh.sendline('bash')
            status = True
        elif re.search("sudo", cred[2]) != None:
            if debug: print("BEETROOT: Trying sudo")
            status = do_sudo(ssh, cred[1])

        if status == False:
            for cred in get_creds(host, ".*,su"):
                if debug: print("BEETROOT: Trying su " + cred[0])
                status = do_su(ssh, cred[1])
                if status == True:
                    continue

        if status == False:
            print "BEETROOT: ERROR: Could not get root on " + host
            exit(4)

        if debug: print "BEETROOT: Got root"
        if command == '':
            do_shell(ssh)
        else:
            do_command(ssh, command)

        do_logout(ssh)

    # These interrupts are generated when the user quits
    except OSError, e:
        print ''
        if debug: print "Exited"

    except KeyboardInterrupt:
        print ''
        if debug: print "User interrupted"

