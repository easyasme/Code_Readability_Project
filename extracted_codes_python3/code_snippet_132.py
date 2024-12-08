#!/usr/bin/python3
import subprocess as sp
from sys import argv
from shlex import split
from argparse import ArgumentParser
import os

cmd_lowp = ['ionice' ,  '-c3' , 'nice' , '-n19']
cmd_sudo = ['sudo']
cmd_e = ['emerge']


options={
'ask'         : [ '--ask'                 , True ],
'verbose'     : [ '--verbose'             , True ],
'bdeps'       : [ '--with-bdeps=y'        , True ],
'keep-going'  : [ '--keep-going=y'        , True ],
'backtrack'   : [['--backtrack=' , 300  ] , True ],
'update'      : [ '--update'              , True ],
'deep'        : [ '--deep'                , True ],
'newuse'      : [ '--newuse'              , True ],
}

## common options
options_common=options.copy()
options_common.pop('update')
options_common.pop('deep')
options_common.pop('newuse')


def list2str(thing):
	s=''
	if type(thing).__name__ == 'list':
		for i in thing:
			s=s+list2str(i)
		return s
	elif type(thing).__name__ == 'str' : return thing
	elif type(thing).__name__ == 'int' : return str(thing)
	else:
		raise Exception('found no str nor list nor int -> error')

def options_list(thing):
	_list=[]
	if type(thing).__name__ =='dict':
		for i in list(thing.keys()):
			if thing[i][1]:
				if type(thing[i][0]).__name__ == 'str':_list.append(thing[i][0])
				elif type(thing[i][0]).__name__ == 'list':_list.append(list2str(thing[i][0]))
				else: raise Exception('found not list nor str -> error')
	else: raise Exception('no dict -> error')
	return _list

###  Setup parser
### look here for actions: argparse._ActionsContainer
description= 'This is the tool "e" that helps to use emerge.\n'
'''       '''+'if dont_know_about_emerge() and want_to_know_about():\n'
'''       '''+'    install_gentoo()\n'
'''       '''+'if not gentoo_is_your_main_system()\n'
'''       '''+'    install_gentoo()'
parser=ArgumentParser(description=description)


#### Task 1 : Emerge reverse dependencies.
parser.add_argument('-r',action='store_true',help='"do some revdep-rebuilding with preserved libs" : Emerge reverse dependencies.')
def task1():
	### generate list of libs
	cmd_q='portageq list_preserved_libs /'
	cmd_ql=split(cmd_q)
	out=sp.check_output(cmd_lowp+cmd_sudo+cmd_ql).decode().splitlines()
	for i in out:
		#i=i.decode()
		print(i)
		print('this task is not fully implemented')

#### Task 2 : @preserved-rebuild
parser.add_argument('-p',action='store_true',help='@preserved-rebuild')
def task2():
	target_set='@preserved-rebuild'
	cmd=cmd_lowp+cmd_sudo+cmd_e+options_list(options_common)+[target_set]
	p=sp.Popen(cmd,stdout=os.fdopen(2),stderr=os.fdopen(1),stdin=os.fdopen(0))

### Run Tasks
args=parser.parse_args()
if args.r:
	task1()

if args.p:
	task2()

#parser.add_argument('-r',action='store_true',help='"emerge @revdep-rebuild" : Emerge reverse dependencies.')
#parser.add_argument('-r',action='store_true',help='"emerge @revdep-rebuild" : Emerge reverse dependencies.')
#parser.add_argument('-r',action='store_true',help='"emerge @revdep-rebuild" : Emerge reverse dependencies.')
#parser.add_argument('-r',action='store_true',help='"emerge @revdep-rebuild" : Emerge reverse dependencies.')



#Notes
#cmd2='portageq list_preserved_libs /'





