#!/usr/bin/env python3
#
# Block Compress https://github.com/burtyb/cb
#
# Chris Burton (c) 2019-2023
#

import argparse, sys, struct, os, hashlib, binascii, time

# Data file version
cfg_version = 0x02

p = argparse.ArgumentParser(description='Compress Blocks')
mode = p.add_mutually_exclusive_group(required=True)
mode.add_argument('-a','--archive', help='Create archive', action='store_true')
mode.add_argument('-x','--extract', help='Extract archive', action='store_true')
mode.add_argument('-l','--list', help='List archive files', action='store_true')
p.add_argument('-b','--block', help='Block size in bytes (default %(default)s)', type=int, default=4096)
p.add_argument('-D', '--debug', help='Show LOTS of debug information', default=False, action='store_true')
p.add_argument('-p','--progress', help="Show progress", default=False, action='store_true')
p.add_argument('-H','--hash', help='Hash algorithm (default %(default)s)', choices=['md5','sha1','sha224','sha256','sha384','sha512'], default='sha1')
p.add_argument('-M','--map', help="Map filename for archive or extract (can be reused) e.g. '-M /dev/sda hdd.img -M /dev/mmcblk1 sd.img'", action='append', nargs=2)
p.add_argument('-c','--compression', help='Builtin compression algorithm', choices=['none','xz','bz2'], default='xz')
p.add_argument('-C','--compressionlevel', help='Compression level 1-9', choices=range(1,10), type=int, default=None)
#p.add_argument('-L','--savelast', help='Save clone pointer to last block instead of first', default=False, action='store_true')
p.add_argument('-v','--verbose', help='Show hash signatures', default=False, action='store_true')
p.add_argument('-S', '--solid', help='Create solid (bigger) archive allowing quicker selective file extract', action='store_true', default=False)
p.add_argument('file', help='In/output archive filename', nargs=1)
p.add_argument('files', help='Files to compress', nargs='*')
args = p.parse_args()

# Disabled option
args.savelast = False
args.map = False

# block size (for archive)
cfg_bs = args.block

# List of files to cleanup if we exit
cleanup = []

# hash options (for archive)
if args.hash=='md5':
	cfg_hash=0x0000
	cfg_hashlen=16
	def h():
		return hashlib.md5()
elif args.hash=='sha1':
	cfg_hashlen=20
	cfg_hash=0x0001
	def h():
		return hashlib.sha1()
elif args.hash=='sha224':
	cfg_hashlen=28
	cfg_hash=0x0002
	def h():
		return hashlib.sha224()
elif args.hash=='sha256':
	cfg_hashlen=32
	cfg_hash=0x0003
	def h():
		return hashlib.sha256()
elif args.hash=='sha384':
	cfg_hashlen=48
	cfg_hash=0x0004
	def h():
		return hashlib.sha384()
elif args.hash=='sha512':
	cfg_hashlen=64
	cfg_hash=0x0005
	def h():
		return hashlib.sha512()

# Return 'format' to read/write the number of bits needed to store the number 'x'
def format_for(x):
	if x.bit_length()>(4*8): # Does it need an unsigned long long (8 bytes)?
		return 'Q'
	elif x.bit_length()>(2*8): # Does it need a unsigned long (4 bytes)?
		return 'L'
	elif x.bit_length()>(1*8): # Does it need a unsigned short (2 bytes)?
		return 'H'
	return 'B' # Otherwise a byte will do

# Archive files
def cmd_archive():
	# If the output file is called '-' write to stdout
	if args.file[0] == '-':
		args.file[0] = '/dev/stdout'

	if args.compression=='xz':
		import lzma
		cfg_comp = 0x01
		if args.compressionlevel:
			clevel=args.compressionlevel
		else:
			clevel=9 # default for xz
		def comp(fn, mode, level):
			return lzma.LZMAFile(fn, mode, preset=level)
	elif args.compression=='bz2':
		import bz2
		cfg_comp = 0x02
		if args.compressionlevel:
			clevel=args.compressionlevel
		else:
			clevel=9 # default for bz2
		def comp(fn, mode, level):
			return bz2.BZ2File(fn, mode, compresslevel=level)
	else: # none
		cfg_comp = 0x00
		clevel=0
		def comp(fn, mode, level):
			return fn

	cfg_options = 0
	if args.solid:
		cfg_options = cfg_options | 0x1

	# Open archive file for output
	if os.path.isfile(args.file[0]) and args.file[0] != '/dev/stdout':
		print("Output archive file already exists", file=sys.stderr )
		sys.exit(1)

	o = open(args.file[0], 'wb')
	
	numfiles = len(args.files)
	numfiles_format = format_for(numfiles)

	# Write archive meta data
	# header "CRB\0" (4 bytes)
	# version  (4 bytes)
	# hash function (2 bytes)
	# hash length (2 bytes)
	# internal compression method (2 bytes)
	# number of files (4 bytes)
	# block size (4 bytes)
	# options (4 bytes)
	o.write(b"CRB\0")
	o.write(struct.pack('>IHHHIII', cfg_version, cfg_hash, cfg_hashlen, cfg_comp, numfiles, cfg_bs, cfg_options ))

	# Enable internal compression if needed
	o = comp(o, "w", clevel)

	files = []
	max_blocks = 0
	total_blocks = 0
	i = 0

	for fn in args.files:
		if args.verbose:
			print( "Input: {}".format(fn), file=sys.stderr )
		finfo = os.stat(fn)

		# If we have a device the size is 0 so try and seek to find the real file size
		if finfo.st_size==0:
			tmp=open(fn,'rb')
			try:
				tmp.seek(0,2)
				fsize=tmp.tell()
			finally:
				tmp.close()
		else:
			fsize=finfo.st_size

		# Remove leading '/' to prevent clobering files
		fn_save = fn.lstrip('/')

		o.write(struct.pack('>I', len(fn_save))) # Length of filename
		o.write( fn_save.encode('utf-8') ) # Filename
		o.write(struct.pack('>Q', fsize)) # unsigned long long (8b) # File Size
		o.write(struct.pack('>Q', int(finfo.st_mtime) )) # unsigned long long (8b) # Modification time
		o.write(struct.pack('>Q', finfo.st_uid)) # unsigned long long (8b) # UID
		o.write(struct.pack('>Q', finfo.st_gid)) # unsigned long long (8b) # GID
		o.write(struct.pack('>Q', 0)) # Byte size of any additional attributes
		# Format of additional attributes
		# 8 byte ID (contact me for a unique ID range)
		# 4 byte bytes len
		# Attribute data

		f = open(fn, 'rb')
		if (fsize/cfg_bs) > max_blocks:
			max_blocks = int(fsize/cfg_bs)

		# dat [file, filename, filesize in blocks, hashlib]
		dat = [ i, f, fn, (fsize/cfg_bs), h() ]

		total_blocks = total_blocks + int(fsize/cfg_bs)

		# If we have a partial block increment number of blocks
		if fsize%cfg_bs:
			dat[3]=dat[3]+1
			total_blocks=total_blocks+1
		files.append(dat)
		i = i + 1

	if args.verbose:
		print("Output: {}".format(args.file[0]), file=sys.stderr )

	block_format = format_for(max_blocks)

	# For each unique hash track the last or first file/block number that used it
	if args.solid:
		# If we're creating solid archive we need a dict for each file
		hashdict = [dict() for x in range(numfiles)]
	else:
		hashdict = [{}]

	# Statistics
	total = 0
	written = 0
	filesleft = numfiles

	if args.progress:
		progress_last_show = int(time.time())

	for block in range(max_blocks+1):
		for file in files:
			if block==(file[3]-1):
				filesleft = filesleft - 1
			if block>(file[3]-1):
				continue
			if args.progress and total!=0 and progress_last_show < int(time.time()):
				tmpstat = os.stat(args.file[0])
				if args.solid:
					hashlen = 0
					for x in range(len(hashdict)):
						hashlen = hashlen + len(hashdict[x])
				else:
					hashlen = len(hashdict[0])
				sys.stderr.write("\r{:3}% {}/{} (c:{} u:{} br:{:.2f} f:{}/{}) r:{:.2f}".format( round(int(100*total/total_blocks),0), total, total_blocks, (total-written), hashlen, float(written)/float(total), filesleft, numfiles, (tmpstat.st_size/(total*cfg_bs)) ))
				progress_last_show = int(time.time())

			buf = file[1].read(cfg_bs)

			file[4].update(buf)

			total = total + 1

			if len(buf) < cfg_bs:
				# PARTIAL BLOCK (< csf_bs)
				o.write( struct.pack('>B', 0x02) )
				o.write( struct.pack('>Q', len(buf)))
				o.write(buf)
			else:
				hash = h()
				hash.update(buf)
				digest = hash.digest()
				if args.solid:
					hashdict_index = file[0]
				else:
					hashdict_index = 0
				if digest in hashdict[hashdict_index]: # CLONE
					o.write( struct.pack('>B', 0x01) ) # Existing block
					dat = hashdict[hashdict_index][digest]
					o.write( struct.pack('>'+numfiles_format, dat[0]) ) # file number
					o.write( struct.pack('>'+block_format, dat[1]) ) # block number
					if args.savelast:
						hashdict[hashdict_index][digest] = [ file[0], block ]
				else: # NEW
					# file number, block number
					hashdict[hashdict_index][digest] = [ file[0], block ]
					o.write( struct.pack('>B', 0x00)) # New block
					o.write(buf)
					written = written + 1

	# Show completed progress bar
	if total!=0 and args.progress:
		tmpstat = os.stat(args.file[0])
		if args.solid:
			hashlen = 0
			for x in range(len(hashdict)):
				hashlen = hashlen + len(hashdict[x])
		else:
			hashlen = len(hashdict[0])
		sys.stderr.write("\r{:3}% {}/{} (c:{} u:{} br:{:.2f} f:{}/{}) r:{:.2f}\n".format( round(int(100*total/total_blocks),0), total, total_blocks, (total-written), hashlen, float(written)/float(total), filesleft, numfiles, (tmpstat.st_size/(total*cfg_bs)) ))
	
	# Write computed hashes for input files
	for file in files:
		if args.verbose:
			print( "{}  {}".format(file[4].hexdigest(), file[2]), file=sys.stderr )
		o.write(file[4].digest())

def cmd_extract():
	# If the input file is called '-' read from stdin
	if args.file[0] == '-':
		args.file[0] = '/dev/stdin'

	if not os.path.isfile(args.file[0]):
		print("Unable to open input file ({})".format(args.file[0]), file=sys.stderr )
		sys.exit(1)

	i = open(args.file[0], 'rb')

	# Read archive metadata

	# Check signature
	signature = i.read(4)
	external_comp = 0
	if signature!=b"CRB\0":
		# Check if we have a compressed file we can deal with
		if signature[0]==0xfd and signature[1]==0x37 and signature[2]==0x7a and signature[3]==0x58:
			i.close()
			if args.verbose:
				print("Detected external xz compression", file=sys.stderr)
			import lzma
			i = lzma.LZMAFile(args.file[0], 'rb')
			signature = i.read(4)
			if signature!=b"CRB\0":
				print("Invalid signature(ZX)", file=sys.stderr)
				sys.exit(1)
			external_comp = 1
		elif signature[0]==0x42 and signature[1]==0x5a and signature[2]==0x68:
			i.close()
			if args.verbose:
				print("Detected external bz2 compression", file=sys.stderr)
			import bz2
			i = bz2.BZ2File(args.file[0], 'rb')
			signature = i.read(4)
			if signature!=b"CRB\0":
				print("Invalid signature(BZ2)", file=sys.stderr)
				sys.exit(1)
			external_comp = 2
		else:
			print("Invalid signature", file=sys.stderr)
			sys.exit(1)

	s_fmt = '>IHHHII'
	s_len = struct.calcsize(s_fmt)
	dat = struct.unpack(s_fmt, i.read(s_len))
	cfg_version     = dat[0]
	cfg_hash        = dat[1]
	cfg_hashlen     = dat[2]
	cfg_comp        = dat[3]
	numfiles        = dat[4]
	cfg_bs          = dat[5]

	if cfg_version>1:
		cfg_options = struct.unpack('>I', i.read(4))
	else:
		cfg_options = 0

	numfiles_format = format_for(numfiles)

	if not (cfg_version == 0x1 or cfg_version == 0x02):
		print("Invalid data version ({})".format(cfg_version), file=sys.stderr)
		sys.exit(1)

	if cfg_hash==0x0000: # md5
		if cfg_hashlen!=16:
			print("Hash length mismatch 16!={}".format(cfg_hashlen), file=sys.stderr)
			sys.exit(1)
		def h():
			return hashlib.md5()
	elif cfg_hash==0x0001: # sha1
		if cfg_hashlen!=20:
			print("Hash length mismatch 20!={}".format(cfg_hashlen), file=sys.stderr)
			sys.exit(1)
		def h():
			return hashlib.sha1()
	elif cfg_hash==0x0002: # sha224
		if cfg_hashlen!=28:
			print("Hash length mismatch 28!={}".format(cfg_hashlen), file=sys.stderr)
			sys.exit(1)
		def h():
			return hashlib.sha224()
	elif cfg_hash==0x0003: # sha256
		if cfg_hashlen!=32:
			print("Hash length mismatch 32!={}".format(cfg_hashlen), file=sys.stderr)
			sys.exit(1)
		def h():
			return hashlib.sha256()
	elif cfg_hash==0x0004: # sha384
		if cfg_hashlen!=48:
			print("Hash length mismatch 48!={}".format(cfg_hashlen), file=sys.stderr)
			sys.exit(1)
		def h():
			return hashlib.sha384()
	elif cfg_hash==0x0005: # sha512
		if cfg_hashlen!=64:
			print("Hash length mismatch 64!={}".format(cfg_hashlen), file=sys.stderr)
			sys.exit(1)
		def h():
			return hashlib.sha512()
	else:
		print("Invalid hash type {}".format(cfg_hash), file=sys.stderr)
		sys.exit(1)

	if cfg_comp==0x01: # xz
		import lzma
		def comp(fn,mode):
			return lzma.LZMAFile(fn, mode)
	elif cfg_comp==0x02: # bz2
		import bz2
		def comp(fn,mode):
			return bz2.BZ2File(fn, mode)
	else: # 0x00 = none
		def comp(fn,mode):
			return fn

	# Enable compression if needed
	i = comp(i, 'rb')

	files = []
	max_blocks = 0
	total_blocks = 0

	extract = []
	# Get metadata for each file
	for j in range(numfiles):
		# TODO combine reads
		# Get filename length
		s_fmt = '>I'
		s_len = struct.calcsize(s_fmt)
		dat = struct.unpack(s_fmt, i.read(s_len))
		fnlen = dat[0]
		# Get filename
		fn = i.read(fnlen).decode('utf-8')

		# Get filesize
		s_fmt = '>Q'
		s_len = struct.calcsize(s_fmt)
		dat = struct.unpack(s_fmt, i.read(s_len) )
		st_size = dat[0]

		s_fmt = '>Q'
		s_len = struct.calcsize(s_fmt)
		dat = struct.unpack(s_fmt, i.read(s_len) )
		st_mtime = dat[0]
		
		s_fmt = '>Q'
		s_len = struct.calcsize(s_fmt)
		dat = struct.unpack(s_fmt, i.read(s_len) )
		st_uid = dat[0]

		s_fmt = '>Q'
		s_len = struct.calcsize(s_fmt)
		dat = struct.unpack(s_fmt, i.read(s_len) )
		aab = dat[0]

		# Read and ignore any additional attribute data
		dat = struct.unpack(s_fmt, i.read(s_len) )
		aab = dat[0]
		i.read(aab)

		fileblocks = int(st_size/cfg_bs)

		fn = fn.lstrip('/')

		if os.path.isfile(fn):
			print("ERROR: file {} already exists".format(fn), file=sys.stderr )
			sys.exit(1)

		if args.verbose:
			print( "Extract: {} ({} bytes)".format(fn, st_size), file=sys.stderr )

		if '/' in fn:
			# Create directory if required and open file ready for read/write
			if not os.path.exists(os.path.dirname(fn)):
				try:
					os.makedirs(os.path.dirname(fn))
				except OSError as exc: # Guard against race condition
					if exc.errno != errno.EEXIST:
						raise
		f = open(fn, 'w+b')

		# index, f, filename, filesize in blocks, hashlib
		dat = [j, f, fn, (st_size/cfg_bs), h() ]

		total_blocks = total_blocks + int(st_size/cfg_bs)

		# If we have a partial block increment number of blocks
		if st_size%cfg_bs:
			dat[3]=dat[3]+1
			fileblocks=fileblocks+1
			total_blocks=total_blocks+1

		if fileblocks>max_blocks:
			max_blocks = fileblocks

		files.append(dat)

		if len(args.files)==0: # If no files listed
			extract.append(dat[0]) # Just add id to extract
		else:
			if fn in args.files:
				extract.append(dat[0]) # Add ID if it's listed in the files to extract

		# If we need to exit remove the output file
		cleanup.append(fn)
	

	if len(extract)<len(args.files):
		print("ERROR: File to extract not found in archive", file=sys.stderr )
		clean_exit()

	block_format = format_for(max_blocks)

	s_fmt = '>B'
	s_len = struct.calcsize(s_fmt)

	if args.progress:
		progress_last_show = int(time.time())

	# Statistics
	written = 0
	
	for block in range(max_blocks):
		for file in files:
			if block>(file[3]-1):
				continue

			if args.progress and written!=0 and progress_last_show < int(time.time()):
				tmpstat = os.stat(args.file[0])
				sys.stderr.write( "\r{:3}% {}/{}".format( round(int(100*written/total_blocks), 0), written, total_blocks) )
				progress_last_show = int(time.time())

			b = struct.unpack(s_fmt, i.read(s_len))
			b = b[0]

			# Ensure we're at the correct place within the file
			if file[1].tell() != (block*cfg_bs):
				print("File position error {} {}".format(file[1].tell(), (block*cfg_bs)), file=sys.stderr )
				sys.exit(1)

			# Process each block type
			if b==0x00: # NEW
				buf = i.read(cfg_bs)
				file[4].update(buf)
				file[1].write(buf)
				if args.debug:
					print( "DEBUG:x:new:[b:{}:f:{}]".format(block,file[0]), file=sys.stderr )
			elif b==0x01: # CLONE
				s_fmti = '>'+numfiles_format+block_format # file_number, block_number
				s_leni = struct.calcsize(s_fmti)
				d = struct.unpack(s_fmti, i.read(s_leni))
				# Save current position of clones source
				offset = files[d[0]][1].tell()
				files[d[0]][1].seek(d[1]*cfg_bs)
				buf = files[d[0]][1].read(cfg_bs)
				files[d[0]][1].seek(offset) # Seek back before trying to write
				file[4].update(buf)
				file[1].write(buf)
				if args.debug:
					print( "DEBUG:x:clone:[b:{}:f:{}]<[b:{}:f:{}]".format(block,file[0],d[1],d[0]), file=sys.stderr )
			elif b==0x02: # PARTIAL
				s_fmti = '>Q'
				s_leni = struct.calcsize(s_fmti)
				d = struct.unpack(s_fmti, i.read(s_leni))
				buf = i.read(d[0])
				file[4].update(buf)
				file[1].write(buf)
				if args.debug:
					print( "DEBUG:x:partial:[b:{}:f:{}:s:{}]".format(block,file[0],d[0]), file=sys.stderr )
			else:
				print("ERROR: unknown block type {}".format(b), file=sys.stderr )
				print("position: {}".format(i.tell()), file=sys.stderr )
				sys.exit(1)
			written=written+1

	if args.progress:
		sys.stderr.write( "\r{:3}% {}/{}\n".format( round(int(100*written/total_blocks), 0), written, total_blocks) )

	hash_ok = True
	for file in files:
		# Get md5 from source file
		tmp = i.read(cfg_hashlen)
		hash_computed = file[4].hexdigest()
		hash_saved    = binascii.hexlify(tmp).decode('ascii')
		if hash_computed==hash_saved:
			status='OK'
		else:
			status='FAILED'
			hash_ok = False
		if args.verbose:
			print("{} {} OK".format(file[2], hash_saved), file=sys.stderr )

	if not hash_ok:
		print("ERROR: Extract hash failure", file=sys.stderr )
		clean_exit()
		

def cmd_list():
	# If the input file is called '-' read from stdin
	if args.file[0] == '-':
		args.file[0] = '/dev/stdin'

	if not os.path.isfile(args.file[0]):
		print("Unable to open input file ({})".format(args.file[0]), file=sys.stderr )
		sys.exit(1)

	i = open(args.file[0], 'rb')

	# Read archive metadata
	signature = i.read(4)
	external_comp = 0
	if signature!=b"CRB\0":
		if signature[0]==0xfd and signature[1]==0x37 and signature[2]==0x7a and signature[3]==0x58:
			i.close()
			if args.verbose:
				print("Detected external xz compression", file=sys.stderr)
			import lzma
			i = lzma.LZMAFile(args.file[0], 'rb')
			signature = i.read(4)
			if signature!=b"CRB\0":
				print("Invalid signature(ZX)", file=sys.stderr)
				sys.exit(1)
			external_comp = 1
		elif signature[0]==0x42 and signature[1]==0x5a and signature[2]==0x68:
			i.close()
			if args.verbose:
				print("Detected external bz2 compression", file=sys.stderr)
			import bz2
			i = bz2.BZ2File(args.file[0], 'rb')
			signature = i.read(4)
			if signature!=b"CRB\0":
				print("Invalid signature(BZ2)", file=sys.stderr)
				sys.exit(1)
			external_comp = 2
		else:
			print("Invalid signature", file=sys.stderr)
			sys.exit(1)

	s_fmt = '>IHHHII'
	s_len = struct.calcsize(s_fmt)
	dat = struct.unpack(s_fmt, i.read(s_len))
	cfg_version     = dat[0]
	cfg_hash        = dat[1]
	cfg_hashlen     = dat[2]
	cfg_comp        = dat[3]
	numfiles        = dat[4]
	cfg_bs          = dat[5]

	if cfg_version>1:
		cfg_options = struct.unpack('>I', i.read(4))
	else:
		cfg_options = 0

	numfiles_format = format_for(numfiles)
	if not (cfg_version == 0x1 or cfg_version == 0x02):
		print("Invalid data version", file=sys.stderr)
		sys.exit(1)

	if cfg_comp==0x01: # xz
		import lzma
		def comp(fn,mode):
			return lzma.LZMAFile(fn, mode)
	elif cfg_comp==0x02: # bz2
		import bz2
		def comp(fn,mode):
			return bz2.BZ2File(fn, mode)
	else: # 0x00 = none
		def comp(fn,mode):
			return fn

	i = comp(i, 'rb')

	files = []
	max_blocks = 0

	filedata = ''
	# Get metadata for each file
	for j in range(numfiles):
		# Get filename length
		s_fmt = '>I'
		s_len = struct.calcsize(s_fmt)
		dat = struct.unpack(s_fmt, i.read(s_len))
		fnlen = dat[0]
		# Get filename
		fn = i.read(fnlen).decode('utf-8')

		# Get filesize
		s_fmt = '>Q'
		s_len = struct.calcsize(s_fmt)
		dat = struct.unpack(s_fmt, i.read(s_len) )
		st_size = dat[0]

		# Get modification time
		s_fmt = '>Q'
		s_len = struct.calcsize(s_fmt)
		dat = struct.unpack(s_fmt, i.read(s_len) )
		st_mtime = dat[0]

		# Get UID
		s_fmt = '>Q'
		s_len = struct.calcsize(s_fmt)
		dat = struct.unpack(s_fmt, i.read(s_len) )
		st_uid = dat[0]

		# Get GID
		s_fmt = '>Q'
		s_len = struct.calcsize(s_fmt)
		dat = struct.unpack(s_fmt, i.read(s_len) )
		st_gid = dat[0]

		# Get length of other attributes
		s_fmt = '>Q'
		s_len = struct.calcsize(s_fmt)
		dat = struct.unpack(s_fmt, i.read(s_len) )
		# Waste any file attributes we don't care about
		i.read(dat[0])

		fileblocks = int(st_size/cfg_bs)

		# If we have a partial block add another block
		if st_size%cfg_bs:
			fileblocks=fileblocks+1

		if fileblocks>max_blocks:
			max_blocks = fileblocks

		fn = fn.lstrip('/')

		filedata=filedata+"file{}:{}:{}:{}:{}:{}\n".format(j, fn, st_size, st_mtime, st_uid, st_gid)

	print("program:Compress Blocks")
	print("version:{}".format(cfg_version))
	print("hash:{}".format(cfg_hash))
	print("hash_len:{}".format(cfg_hashlen))
	print("compression:{}:{}".format(cfg_comp, external_comp))
	print("numfiles:{}".format(numfiles))
	print("block_size:{}".format(cfg_bs))
	print("block_bits:{}:{}".format(max_blocks.bit_length(), format_for(max_blocks)))
	print("file_bits:{}:{}".format(numfiles.bit_length(), format_for(numfiles)))
	print(filedata, end='')

# If we need to exit after we've opened output files remove them before exit
def clean_exit():
	for f in cleanup:
		os.remove(f)
	sys.exit(2)

# Mode

if args.extract:
	cmd_extract()
elif args.archive:
	if len(args.files)<1:
		print("ERROR: Missing files to archive", file=sys.stderr)
		sys.exit(2)
	cmd_archive()
elif args.list:
	cmd_list()
else:
	print("ERROR: Missing command??", file=sys.stderr)
	sys.exit(2)
