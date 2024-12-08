#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set noexpandtab tabstop=4:

"""
tx - unpack multiple compressed file types

Public domain.

Juho Hämäläinen 2008-2024 jusa@hilvi.org

"""

import os
import subprocess
import sys
import re
from optparse import OptionParser, SUPPRESS_HELP
from subprocess import DEVNULL

VERSION = "1.4.2"

DEFAULT_COMPRESS_TYPE   = "tar.gz"

Verbose                 = 1
FileList                = 2
Archive                 = 3

verbose_print = False

class Handler:
	def __init__(self, name, binaries, desc, compress, uncompress, list_contents, verbose, quiet, ext):
		self.name = name
		self.binaries = binaries
		self.desc = desc
		self.compress = compress
		self.uncompress = uncompress
		self.list_contents = list_contents
		self.verbose = verbose
		self.quiet = quiet
		self.ext_r = ext
		self.ext_compiled = []

	def ext(self):
		if len(self.ext_compiled) == 0:
			for e in self.ext_r:
				self.ext_compiled.append(re.compile(e))
		return self.ext_compiled

ftypes_list = None

def ftypes():
	global ftypes_list
	if ftypes_list:
		return ftypes_list

	ftypes_list = [
		Handler('tar',
		        ['tar'],
		        'Tar archive.',
		        [ 'tar', Verbose, '-c -f', Archive, FileList ],
		        [ 'tar', Verbose, '-x -f', Archive ],
		        [ 'tar -v --list -f', Archive ],
		        '-v',
		        '',
		        [r'\.tar$']),
	
		Handler('tar.gz',
		        ['tar', 'gzip'],
		        'Tar archive compressed with gzip.',
		        [ 'tar', Verbose, '-c -z -f', Archive, FileList ],
		        [ 'tar', Verbose, '-x -z -f', Archive ],
		        [ 'tar -v -z --list -f', Archive ],
		        '-v',
		        '',
		        [r'\.tar\.gz$', '\.tgz$']),
	
		Handler('tar.bz2',
		        ['tar', 'bzip2'],
		        'Tar archive compressed with bzip2.',
		        [ 'tar', Verbose, '-c -j -f', Archive, FileList ],
		        [ 'tar', Verbose, '-x -j -f', Archive ],
		        [ 'tar -v -j --list -f', Archive ],
		        '-v',
		        '',
		        [r'\.tar\.bz2$', r'\.tbz2$']),
	
		Handler('tar.xz',
		        ['tar', 'xz'],
		        'Tar archive compressed with xz.',
		        [ 'tar', Verbose, '-c -J -f', Archive, FileList ],
		        [ 'xz -d -c', Archive, '| tar -x', Verbose ],
		        [ 'xz -d -c', Archive, '| tar -v --list' ],
		        '-v',
		        '',
		        [r'\.tar\.xz$', r'\.txz$']),
	
		Handler('tar.lz',
		        ['tar', 'lunzip'],
		        'Tar archive compressed with lzip.',
		        None,
		        [ 'tar', Verbose, '-x --lzip -f', Archive ],
		        [ 'tar -v -x --lzip --list -f', Archive ],
		        '-v',
		        '',
		        [r'\.tar\.lz$']),
	
		Handler('tar.lz4',
		        ['tar', 'lz4'],
		        'Tar archive compressed with lz4.',
		        [ 'tar', Verbose, '-c', FileList, '| lz4 -f -z -', Archive ],
		        [ 'lz4 -d', Archive, '-c | tar -x', Verbose ],
		        [ 'lz4 -d', Archive, '-c | tar -v --list' ],
		        '-v',
		        '',
		        [r'\.tar\.lz4$']),
	
		Handler('gz',
		        ['gzip'],
		        'File compressed with gzip.',
		        [ 'gzip', Verbose, '-c >', Archive, '<', FileList ],
		        [ 'gzip', Verbose, '-d -k', Archive ],
		        None,
		        '-v',
		        '',
		        [r'\.gz$']),
	
		Handler('bz2',
		        ['bzip2'],
		        'File compressed with bzip2.',
		        [ 'bzip2', Verbose, '-c >', Archive, '<', FileList ],
		        [ 'bzip2', Verbose, '-d -k', Archive ],
		        None,
		        '-v',
		        '',
		        [r'\.bz2$']),
	
		Handler('xz',
		        ['xz'],
		        'Xz archive.',
		        [ 'xz', Verbose, '-c >', Archive, '<', FileList ],
		        [ 'xz', Verbose, '-d -k', Archive ],
		        None,
		        '-v',
		        '',
		        [r'\.xz$']),
	
		Handler('lz4',
		        ['lz4'],
		        'LZ4 archive',
		        [ 'lz4', Verbose, '-c >', Archive, '<', FileList ],
		        [ 'lz4', Verbose, '-k -d', Archive ],
		        None,
		        '',
		        '-q',
		        [r'\.lz4$']),
	
		Handler('zip',
		        ['unzip'],
		        'Zip archive.',
		        [ 'zip', Verbose, '-r', Archive, FileList ],
		        [ 'unzip', Verbose, Archive ],
		        [ 'unzip -v -l', Archive ],
		        '',
		        '-q',
		        [r'\.zip$']),
	
		Handler('rar',
		        ['unrar'],
		        'Rar archive.',
		        None,
		        [ 'unrar x', Archive ],
		        None,
		        None,
		        None,
		        [r'\.rar$']),
	
		Handler('ace',
		        ['unace'],
		        'Ace archive.',
		        None,
		        [ 'unace x', Archive ],
		        None,
		        None,
		        None,
		        [r'\.ace$']),
	
		Handler('arj',
		        ['arj'],
		        'Arj archive.',
		        [ 'arj a', Archive, FileList ],
		        [ 'arj x -i', Archive ],
		        None,
		        None,
		        None,
		        [r'\.arj$']),
	
		Handler('deb',
		        ['dpkg-deb'],
		        'Debian package.',
		        None,
		        [ 'dpkg-deb -x', Archive, '.' ],
		        None,
		        None,
		        None,
		        [r'\.deb$']),
	
		Handler('dsc',
		        ['dpkg-source'],
		        'Debian source package.',
		        None,
		        [ 'dpkg-source -x', Archive ],
		        None,
		        None,
		        None,
		        [r'\.dsc$']),
	
		Handler('rpm',
		        ['rpm2cpio', 'cpio'],
		        'Rpm package.',
		        None,
		        [ 'rpm2cpio', Archive, "| cpio -idm", Verbose ],
		        [ 'rpm2cpio', Archive, "| cpio -idm --verbose --list" ],
		        '',
		        '--quiet',
		        [r'\.rpm$']),
	
		Handler('7z',
		        ['7z'],
		        '7zip package.',
		        [ '7z a', Archive, FileList ],
		        [ '7z x', Archive ],
		        None,
		        None,
		        None,
		        [r'\.7z$']),
	
		Handler('exe',
		        ['innoextract'],
		        'Inno Setup package (.exe).',
		        None,
		        [ 'innoextract -s', Archive ],
		        None,
		        None,
		        None,
		        [r'\.exe$']),
	
		Handler('rcore',
		        ['rich-core-extract'],
		        'Rich core.',
		        None,
		        [ 'rich-core-extract', Archive ],
		        [ 'lzop -v -l', Archive ],
		        None,
		        None,
		        [r'\.rcore$', r'\.rcore\.lzo$', r'\.rcore\.gz$']),
	
		Handler('lzo',
		        ['lzop'],
		        'Lempel-Ziv-Oberhumer packer.',
		        None,
		        [ 'lzop -d', Archive ],
		        [ 'lzop -v -l', Archive ],
		        None,
		        None,
		        [r'\.lzo$']),
	
		Handler('apk',
		        ['apktool'],
		        'Android application package.',
		        None,
		        [ 'apktool decode', Archive ],
		        None,
		        None,
		        None,
		        [r'\.apk$']),
	]

	return ftypes_list

def vprint(*args):
	if verbose_print:
		print("#- ", end='')
		print(*args)

def eprint(*args):
	print(*args, file=sys.stderr)

def iteritems(d):
	try:
		items = d.iteritems()
	except AttributeError:
		items = d.items()
	return items

def files_exist(file_list, compress):
	missing = []
	for f in file_list:
		if not compress and os.path.isfile(f):
			continue
		if compress and os.path.exists(f):
			continue
		missing.append(f)
	if len(missing) > 0:
		return ", ".join(missing)
	return None

def check_binary(exe):
	return subprocess.call(["which", exe], stdout=DEVNULL, stderr=subprocess.STDOUT) == 0

def check_binaries(handler, print_error=True):
	ret = True
	for b in handler.binaries:
		if not check_binary(b):
			eprint("Binary not in PATH '%s'" % b)
			ret = False
	return ret

def find_handler(filename, force_type=None, print_error=True):
	handler = None
	ext = None
	if force_type:
		filetype = force_type
	else:
		filetype = filename
	for h in ftypes():
		for r in h.ext():
			# nice workaround for shortcoming of re.match() not being
			# able to match other than starting from beginning of string..
			if len(r.split(filetype, maxsplit=1)) == 2:
				handler = h
				ext = r
				break
		if handler:
			break
	if not handler:
		if print_error:
			fname = filename
			if force_type:
				fname = "%s%s" % (filename, force_type)
			eprint("No handler for '%s'" % fname)
	else:
		if not check_binaries(handler, print_error):
			handler = None
	return (handler, ext)

def find_verbose_switch(handler):
	verbose_switch = None
	if handler.verbose or handler.quiet:
		verbose_switch = ""
	if verbose_print and handler.verbose:
		verbose_switch = handler.verbose
	elif not verbose_print and handler.quiet:
		verbose_switch = handler.quiet
	return verbose_switch

def build_cmd(handler, args, archive, file_list = None):
	cmd = []
	for arg in args:
		if isinstance(arg, int):
			if arg == Verbose:
				verbose_switch = find_verbose_switch(handler)
				if verbose_switch:
					cmd.append(verbose_switch)
			elif arg == FileList:
				cmd.append(file_list)
			elif arg == Archive:
				cmd.append('"%s"' % archive)
		else:
			cmd.append(arg)
	return ' '.join(cmd)

def extract(cwd, filename, force_type):
	handler, _ = find_handler(filename, force_type)
	err = 1
	if cwd:
		err = os.system("[ -d '%s' ]" % cwd)
		if err != 0:
			eprint("No such directory or cannot enter ’%s’" % cwd)
			return err
	err = 1
	if handler:
		if not os.path.isabs(filename):
			filename = "/".join([os.getcwd(), filename])
		cmd = build_cmd(handler, handler.uncompress, filename)
		if cwd:
			cmd = "cd '%s' && %s" % (cwd, cmd)
		vprint(cmd)
		err = os.system(cmd)
	return err

def compress(archive, filenames, force_type):
	err = 1

	handler = None
	# If no filenames are passed try to autodetect the directory
	# or file to compress and what the file format should be.
	if len(filenames) == 0:
		compress_type = DEFAULT_COMPRESS_TYPE
		# If user passes for example -c my_dir.tar.lz4 first try to
		# find handler for .tar.lz4, and if handler is found, see if
		# there exists file or directory with name my_dir
		if not force_type:
			handler, ext = find_handler(archive, print_error=False)
			if handler:
				basename = re.sub(ext, '', archive)
				if os.path.exists(basename):
					archive = basename
					compress_type = handler.name
		if os.path.exists(archive):
			filenames = [ os.path.normpath(archive) ]
			if not handler and force_type:
				handler, _ = find_handler(archive, force_type)
				if not handler:
					return err
				compress_type = handler.name
			archive = str.format("{}.{}", os.path.normpath(archive), compress_type)
			if verbose_print:
				print("Compressing to %s as archive type %s..." % (archive, compress_type))
		else:
			eprint("No files listed for archive.")
			return err

	if not handler:
		handler, _ = find_handler(archive, force_type)
	if handler and not handler.compress:
		eprint("Compression not supported with %s." % handler.name)
		return err
	if handler:
		escaped = list(map(lambda s: str.format("\"{}\"", os.path.normpath(s)), filenames))
		file_list = " ".join(escaped)
		cmd = build_cmd(handler, handler.compress, archive, file_list)
		vprint(cmd)
		err = os.system(cmd)
	return err

def list_contents(filename):
	err = 1
	handler, _ = find_handler(filename)
	if handler and not handler.list_contents:
		eprint("Listing contents is not supported with %s." % handler.name)
		return err
	if handler:
		cmd = build_cmd(handler, handler.list_contents, False, filename)
		err = os.system(cmd)
	return err

def print_extensions():
	for handler in ftypes():
		missing = []
		for b in handler.binaries:
			if not check_binary(b):
				missing.append(b)
		if len(missing) > 0:
			ok = "[%s needed]" % ",".join(missing)
		else:
			ok= "[OK]"
		print("%-*s %-*s %s" % (12, handler.name, 48, handler.desc, ok))

def print_autocomplete():
	handled = []
	for handler in ftypes():
		available = True
		for b in handler.binaries:
			if not check_binary(b):
				available = False
				break
		if available:
			for i in handler.ext_r:
				handled.append(i.replace('\.', '.').replace('$', '')[1:])
	print('|'.join(handled))

def main():
	parser = OptionParser(usage="""\
usage: %prog [options] files...

(Un)pack multiple compressed file types with single
program.
""", version="%%prog %s" % VERSION)

	parser.add_option('-v', '--verbose',
		action='store_true',
		dest='verbose',
		default=False,
		help="""be verbose about operation""")
	parser.add_option('-t', '--types',
		action='store_true',
		dest='list_types',
		default=False,
		help="""list handled filetypes""")
	parser.add_option('-f', '--force',
		action='store',
		type='string',
		dest='type',
		help="""force archive type""")
	parser.add_option('-c', '--compress',
		action='store',
		type='string',
		dest='archive',
		default=None,
		help="""compress files to archive, if only target is specified and a file or
directory by that name exists an archive is created consisting solely
of this file or directory""")
	parser.add_option('-l', '--list',
		action='store_true',
		dest='list_contents',
		default=False,
		help="""List files in archive.""")
	parser.add_option('-C', '--change-dir',
		action='store',
		type='string',
		dest='change_dir',
		default=None,
		help="""change to directory before extracting""")
	parser.add_option('', '--autocomplete-types',
		action='store_true',
		dest='list_autocomplete_types',
		default=False,
		help=SUPPRESS_HELP)
	
	opts, args = parser.parse_args()
	
	if opts.list_types:
		print_extensions()
		sys.exit(0)
	elif opts.list_autocomplete_types:
		print_autocomplete()
		sys.exit(0)

	if len(args) == 0 and not opts.archive:
		parser.print_help()
		sys.exit(199)

	missing = files_exist(args, opts.archive)
	if missing:
		eprint("file(s) not found: %s" % missing)
		sys.exit(200)

	force = None
	if opts.type:
		force = ".%s" % opts.type

	global verbose_print
	verbose_print = opts.verbose

	ret = 0
	if opts.archive:
		if opts.list_contents:
			eprint("--list cannot be used with --compress")
			sys.exit(1)
		ret = compress(opts.archive, args, force_type=force)
	else:
		for i in args:
			if opts.list_contents:
				ret = list_contents(i)
			else:
				ret = extract(opts.change_dir, i, force_type=force)
			if ret != 0:
				sys.exit(ret)

	sys.exit(ret)

if __name__ == "__main__":
	main()

