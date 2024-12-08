import os
import argparse
import shutil
import sys
JTF = argparse.ArgumentParser(description="Dump Minecraft Assets Files")
JTF.add_argument('version',type=str,help="choose minecraft a version.",metavar='Version',default='list_subete',nargs='?')
JTF.add_argument('-l','--list',help="list all avaliable version",action='store_true',dest='list')
JTF.add_argument('-d','--dir',type=str,help='set the .minecraft directory manually. By default use default directory.',default='false',metavar='<dir>',dest='mc_dir')
def split_to_list(json_dir):
   with open(str(json_dir)) as f:
      data = f.read()
   strlist = data .split('}, "')
   json_list = []
   a = 0
   for line in strlist:
      json_list.append(line.lstrip('{"objects": {"'))
      a = a +1
   return json_list

def list_to_line(line,type):
   run = 0
   tri = 1
   sct = 1
   json_dump_path = []
   json_dump_source = []
   for string in line:
      string = str(string)
      x = string.split(', ')
      for y in x:
         run = run + 1
         if run == sct:
            sct = sct + 2
            spp = y.split(': {"hash":')
            for sop in spp:
               if run == tri:
                  tri = tri + 2
                  z = sop.rstrip('"')
                  s = z.lstrip(' "')
                  json_dump_path.append(s)
               else:
                  o = sop.lstrip(' "')
                  p = o.rstrip('" ')
                  json_dump_source.append(p)
   if type == '1':
      return json_dump_source
   if type == '2':
      return json_dump_path

def mkdup2(list):
   list_dup = [] 
   for line in list:
      e = line[0:2]
      list_dup.append('objects' + '/' + e + '/' + line)
   print('step1 complete')
   return(list_dup)

def dup2(path,dup,mcpath,version):
   t = path
   y = dup
   a = 0
   for line in t:   
      try:
         os.makedirs('assets' + version + '/' + y[a])
         os.rmdir('assets' + version + '/' + y[a])
         shutil.copy(str(mcpath + '/assets/' + t[a]), 'assets' + version + '/' + y[a])
         a = a + 1
         #print('No.',a,'The',y[a-1],'Completed')
      except:
         i = open('Errors.txt','w')
         a = a + 1
         c = str(a)
         i.write(c)
         i.write(t[a-1])
         i.write('复制到')
         i.write(y[a-1])
         i.write('的过程中出现错误\n')
         print('No.',a,'From',mcpath + '/assets/' + t[a-1],'To','assets' + version + '/' + y[a],'Unkown Error')
         i.close
   print('step2 complete')

args = JTF.parse_args()
ntdir = str('/AppData/Roaming/.minecraft')
homedir = str(os.path.expanduser('~'))
if os.name == 'nt':
   mcdir = homedir + ntdir
if os.name == 'posix':
   mcdir = homedir + '/.minecraft'
if args.mc_dir != 'false':
   mcdir = args.mc_dir
   if os.path.isdir(str(mcdir + '/assets/')) == False:
      mcdir = mcdir + '/.minecraft'

indexes_dir = mcdir + '/assets/indexes/' + args.version  + '.json'
print(indexes_dir)
if args.list == True:
   print('list of all avaliable version') 
   for f in os.listdir(mcdir + '/assets/indexes/'):
      print(f.rstrip('.json'),end=",  ")
   sys.exit(0)
if args.version == 'list_subete':
   if os.path.exists(indexes_dir) == False:
      print('Can not find minecraft assets files.')
      JTF.print_help()
      sys.exit(0)
   print('list of all avaliable version')
   for f in os.listdir(mcdir + '/assets/indexes/'):
      print(f.rstrip('.json'),end=",  ")
   print()
   JTF.print_help()
   sys.exit(0)
if os.name == "nt":
   print("System ==> Windows")
if os.name == "posix":
   print("System ==> *NIX")
print('MC dir ==>',mcdir)
if args.version != 'list_subete':
   if os.path.exists(indexes_dir) == True:
      dup2(mkdup2(list_to_line(split_to_list(indexes_dir),'1')),list_to_line(split_to_list(indexes_dir),'2'),mcdir,args.version)
      sys.exit(0)
   print('This version had not been installed.')
   sys.exit(0)
