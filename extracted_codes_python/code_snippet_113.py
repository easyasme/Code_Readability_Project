#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import fcntl
import signal
import struct
import termios
import platform
from json import dump, load
from collections import defaultdict
from optparse import OptionParser

# check pexpect
try:
    import pexpect
except ImportError:
    print("You have to install 'pexpect' package before running")
    sys.exit(1)

HOSTS = {}
ALIAS = {}

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.goo')
HOST_FILE = os.path.join(CONFIG_DIR, 'hosts')
ALIAS_FILE = os.path.join(CONFIG_DIR, 'alias')


def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.system('rm -rf %s' % dirname)
        os.makedirs(dirname, 0o700)


def ensure_file(filename):
    if not os.path.isfile(filename):
        os.system('rm -rf %s' % filename)
        with open(filename, 'w') as fp:
            dump({}, fp)


def check_record(_func):
    '''check the host and alias record file'''
    ensure_dir(CONFIG_DIR)
    ensure_file(HOST_FILE)
    ensure_file(ALIAS_FILE)

    def wrapper(*args, **kwargs):
        return _func(*args, **kwargs)

    return wrapper


@check_record
def save_conf():
    with open(HOST_FILE, 'w') as hosts_fp:
        dump(HOSTS, hosts_fp, indent=4, sort_keys=True)
    with open(ALIAS_FILE, 'w') as alias_fp:
        dump(ALIAS, alias_fp, indent=4, sort_keys=True)


@check_record
def read_conf():
    global HOSTS, ALIAS

    with open(HOST_FILE, 'r') as hosts_fp:
        try:
            HOSTS = load(hosts_fp)
        except ValueError:
            HOSTS = {}
    with open(ALIAS_FILE, 'r') as alias_fp:
        try:
            ALIAS = load(alias_fp)
        except ValueError:
            ALIAS = {}


def assign_alias(host, alias):
    '''assign a alias to the host'''
    global HOSTS, ALIAS
    if host in HOSTS:
        if alias in ALIAS and ALIAS[alias] != host:
            print('You already assign "%s" to "%s"' % (alias, ALIAS[alias]))
            times = 3
            ensure = raw_input('Are you sure re-assign it to "%s"? (y/n) ' % host).upper()
            while times > 0:
                if ensure in ['Y', 'YES']:
                    break
                elif ensure in ['N', 'NO', '\n', '']:
                    sys.exit(0)
                else:
                    ensure = raw_input('Please type "y" or "n": ').lower()
                times -= 1
            else:
                print('Wrong type')
                sys.exit(0)
        ALIAS[alias] = host
        save_conf()
    else:
        print('There is no record of this host')


def delete(name):
    if name in ALIAS:
        ALIAS.pop(name)
        save_conf()
    elif name in HOSTS:
        HOSTS.pop(name)
        for als, host in ALIAS.copy().items():
            if host == name:
                ALIAS.pop(als)
        save_conf()
    else:
        print('Not record this alias or host')


def record_host(host, user, password, port, key):
    '''record successful login info of the host'''
    global HOSTS
    if host not in HOSTS:
        HOSTS[host] = {'user': user}
        if password:
            HOSTS[host]['password'] = password
        if key:
            HOSTS[host]['key'] = key
        if port != 22:
            HOSTS[host]['port'] = port
        save_conf()


def get_host_info(host):
    host_info = {}
    if host in ALIAS:
        host = ALIAS[host]
    if host in HOSTS:
        host_info.update(HOSTS[host])
        host_info['host'] = host
        return host_info


def show_hosts():
    alias_dict = defaultdict(set)
    for als, host in ALIAS.items():
        alias_dict[host].add(als)

    if HOSTS:
        print('You manage these hosts:')
        print('   %s %s' % ('Host'.ljust(16), 'Alias'))
        print('-' * 27)

        sort_key = lambda ip: ([int(i) for i in ip.split('.')]
                               if re.match(r'^(?:\d+.){3}\d+$', ip)
                               else ip)

        for host in sorted(HOSTS.keys(), key=sort_key):
            als = sorted(alias_dict.get(host, ''))
            print('   %s %s' % (host.ljust(16), ', '.join(als)))
    else:
        print("You don't have any host")


def set_window_size(expect):
    '''set expect window size'''
    s = struct.pack("HHHH", 0, 0, 0, 0)
    a = struct.unpack(
        'hhhh',
        fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
    )
    expect.setwinsize(a[0], a[1])


def sigwinch_passthrough(sig, data):
    global ssh
    set_window_size(ssh)


def login(host, user, password=None, port=22, key=None, alias=None):
    global ssh
    if key:
        cmd = 'ssh -p %s -i %s %s@%s' % (port, key, user, host)
    else:
        cmd = 'ssh -p %s %s@%s' % (port, user, host)
    ssh = pexpect.spawn(cmd)
    set_window_size(ssh)

    prompts = [
        '(?i)are you sure you want to continue connecting.*',
        '%s.*password:.*' % user,
        "(?i)permission denied",
        '(?i)network is unreachable',
        '(?i)connection refused',
        '(?i)connection closed by remote host',
        '(?i)welcome to',
        '(?i)last login:',
    ]

    while True:
        try:
            index = ssh.expect(prompts, timeout=30)

            if index == 0:
                print('Are you sure you want to continue connecting: yes')
                ssh.sendline('yes')
            elif index == 1:
                if password is None:
                    ssh.terminate()
                    print('Password is None')
                    sys.exit(1)
                ssh.sendline(password)
            elif index == 2:
                ssh.terminate()
                print('The password is wrong')
                sys.exit(1)
            elif index == 3:
                ssh.terminate()
                print('Network is unreachable')
                sys.exit(1)
            elif index == 4:
                ssh.terminate()
                print('Connection refused')
                sys.exit(1)
            elif index == 5:
                ssh.terminate()
                print('Connection closed by remote host')
                sys.exit(1)
            elif index in [6, 7]:
                print({6: 'Welcome to', 7: 'Last login:'}[index],
                      end='', flush=True)
                record_host(host, user, password, port, key)
                if alias is not None:
                    assign_alias(host, alias)
                if platform.system() == 'Linux':
                    os.system('notify-send "Go to :  %16s"' % host)
                break
        except KeyboardInterrupt:
            print('User cancel')
            ssh.terminate()
            sys.exit(0)
        except (pexpect.TIMEOUT, pexpect.EOF) as e:
            print('Timeout, server %s not responding.' % host)
            print('--------------------')
            print('[BUFFER]: %s' % ssh.buffer)
            print('[BEFORE]: %s' % ssh.before)
            print('[AFTER] : %s' % ssh.after)
            print('--------------------')
            ssh.terminate(force=True)
            sys.exit(1)

    try:
        ssh.interact()
    except Exception as e:
        ssh.terminate(force=True)
        print(e)
        sys.exit(1)


def ssh_exit(sig, frame):
    global ssh
    ssh.terminate()
    sys.exit(0)


if __name__ == '__main__':
    # load conf
    read_conf()

    # parse args
    opt = OptionParser()
    opt.add_option('-a', dest='alias', help=u'alias of the host')
    opt.add_option('-d', dest='delete', help=u'delete a host or alias')
    opt.add_option('-l', dest='show', action='store_true', default=False,
                   help=u'show your host list')
    opt.add_option('-k', dest='key', help=u'key file')
    opt.add_option('-p', dest='port', default=22, help=u'the host port')
    options, args = opt.parse_args()

    alias = options.alias
    del_name = options.delete
    show = options.show
    key = options.key
    port = options.port

    # check the delete arg
    if del_name:
        delete(del_name)
        sys.exit(0)

    # check the show arg
    if show is True:
        show_hosts()
        sys.exit(0)

    # check ssh
    try:
        ssh = pexpect.spawn('ssh')
    except:
        print("You have to install 'ssh' package before running")
        sys.exit(1)

    signal.signal(signal.SIGWINCH, sigwinch_passthrough)
    signal.signal(signal.SIGHUP, ssh_exit)
    signal.signal(signal.SIGINT, ssh_exit)
    signal.signal(signal.SIGTERM, ssh_exit)

    n = len(args)
    if n == 0 and ALIAS.get('DEF'):
        als = ALIAS.get('DEF')
        login_info = get_host_info(als)
        if login_info:
            login(**login_info)
        else:
            opt.print_help()
    elif n == 1:
        login_info = get_host_info(args[0])
        if login_info:
            if alias:
                assign_alias(login_info['host'], alias)
            else:
                login(**login_info)
        else:
            print('There is no record of this host')

    elif n == 2:
        host, user = args
        login(host, user, port=port, key=key, alias=alias)

    elif n == 3:
        host, user, password = args
        login(host, user, password, port=port, key=key, alias=alias)
    else:
        opt.print_help()
