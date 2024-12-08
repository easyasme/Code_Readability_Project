#!/usr/bin/python3

memfilep="/dev/shm/xdisplay_modifications"
xcalib_args_reset  = ['-c','-a']
xcalib_args_invert = ['-i','-a']
xcalib_cmdbase=['xcalib']

from sys import path
from os import environ
path.append(environ['HOME']+'/code/pylib/pylib')
from pylib import du
from pylib.screen_utils import get_connected_output_count_at_env_layout_index
from sys import stdout,exit,stderr
du.file=stdout
from pylib.du import dd,d0,d1
from sys import argv
from os import stat,chmod
from warnings import warn
from subprocess import check_call

def parse_args():
    global args
    args={'reset':False,'screen_index': None }
    for a in argv[1:]:
        if a == "-r":
            args['reset']=True
        else:
            args['screen_index']=int(a)-1

parse_args()
data_key=str(args['screen_index'])
outp_index,x_display=get_connected_output_count_at_env_layout_index(args['screen_index'],return_x_display=True)
xcalib_output_args=['-o',str(outp_index)]

def check_perms():
    counter=0
    perms_to_check = None
    while perms_to_check != '00':
        counter+=1
        try:
            perms=oct(stat(memfilep).st_mode)
        except FileNotFoundError:
            with open(memfilep,'w'):
                pass
            chmod(memfilep,0o0700)
            perms=oct(stat(memfilep).st_mode)
        
        perms_to_check=perms[-2:]
        if perms_to_check != '00':
            # delete all potentially evil code
            with open(memfilep,'wb') as f:
                pass
            warning_msg="\n" \
                + "## WARNING ##\n" \
                + "    file permissions were wrong and file was not empty\n" \
                + "    emptied the file to sure no evil code is in it.\n" \
                + "    filepath: " + memfilep +"\n"
            warn(warning_msg)
            chmod(memfilep,0o0700)
        if counter>3:
            print("ERROR: could not fix permissions of memfile",file=stderr)
            exit(1)
check_perms()

inverted=None
with open(memfilep,'rb+') as f: 
    data=f.read()
    if len(data) > 0 :
        data=eval(data)
        if data_key in data.keys() and 'inverted' in  data[data_key].keys():
            inverted=data[data_key]['inverted']
    else:
        data={}
    if args['reset']:
        cmd=xcalib_cmdbase+xcalib_output_args+xcalib_args_reset
    else:
        cmd=xcalib_cmdbase+xcalib_output_args+xcalib_args_invert
    env=environ.copy()
    env.update({"DISPLAY":x_display})
    check_call(cmd,env=env)
    if args['reset']:
        inverted = False
    elif inverted is None:
        inverted = True
    else:
        inverted = not inverted
    f.seek(0)
    data.update({data_key:{'inverted': inverted }})
    f.write((repr(data)+"\n").encode())
    print("inverted: "+str(inverted))
