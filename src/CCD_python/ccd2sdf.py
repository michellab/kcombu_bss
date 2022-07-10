#!/usr/bin/env python
##
## <ccd2sdf.py>
##



import sys
import re
import math
import os
import glob
from datetime import datetime

LastModDate = '2020/04/01'


def read_option(argv,opt_dic):
  opt_dic['COMMAND'] = argv[0]
  now = datetime.now()
  opt_dic['START_DATE'] = now.strftime("%Y/%m/%d %H:%M:%S")
  for i in range(1,len(argv)):
    opt_dic['COMMAND'] += ' '
    opt_dic['COMMAND'] += argv[i]
    if (argv[i][0]=='-'):
      if ((i+1)<len(argv)):
        opt_dic[argv[i][1:]] = argv[i+1]




def output_converted_SDF_file(iciffile,comp_id,oSDFdir,opt_subdir,opt_action,type2D3D,avoidexist):
  if (opt_subdir =='T'):
    osdfdir  = oSDFdir + '/' + comp_id[0]
    osdffile = oSDFdir + '/' + comp_id[0] + '/' + comp_id + '.sdf'
  else:
    osdfdir  = oSDFdir 
    osdffile = oSDFdir + '/' + comp_id + '.sdf'

  command = "%s -A %s -osdf %s"%(OPT.get('ckcombu','ckcombu'),iciffile,osdffile)
  if (type2D3D == '2D'):
    command = command + " -gen2d T"

  if (os.path.exists(osdfdir)==0):
    print "#mkdir '%s'"%(osdfdir)
    if (opt_action == 'T'):
      os.mkdir(osdfdir)
    else:
      print "#command_to_be_executed 'mkdir %s'"%(osdfdir)

  fileout = 1
  if (avoidexist == 'T') and (type2D3D == '2D'):
    if (os.path.exists(osdffile)):
      fileout = 0
             
 
  if (fileout == 1): 
    if (opt_action == 'T'):
      print "#execute_command '%s'"%(command)
      os.system(command)
    else: 
      print "#command_to_be_executed '%s'"%(command)
  else:
    print "#SDFfile '%s' already exists. Do nothing."%(osdffile)


def read_list_file(ifname):
  idlist = []
  f = open(ifname)
  for line in f:
    if (len(line)>1) and (line.startswith('#')==0):
       line = line.rstrip('\n')
       fields = line.split()
       idlist.append(fields[0])  
  f.close()
  return(idlist)

def select_files_by_ids(filelist,idlist):
  new_filelist = []
  for fname in (filelist):
    fields = fname.split('/')
    (ID, tail) = fields[-1].split('.') 
    if (ID in idlist):
      new_filelist.append(fname)
  return(new_filelist)


###############
#### MAIN #####
###############

OPT = {}
OPT['icifdir'] = 'tmpout'
OPT['subdir'] = 'T'
OPT['osdf2D'] = ''
OPT['osdf3D'] = ''
OPT['A'] = 'F'
OPT['ckcombu'] = '/home/takawaba/work/kcombu/ckcombu'
OPT['avoexist'] = 'T'
OPT['olog'] = 'ccd2sdf.log'
OPT['div'] = '0/1'

if (len(sys.argv)<3):
  print "ccd2sdf.py <options>"
  print " code by T.Kawabata. LastModified:%s"%(LastModDate)
  print " for converting a chamical component dictionary (CCD) cif files into 2D/3D SDF files"
  print "<options>"
  print "  -icifdir :input cif directory [%s]"%(OPT.get('icifdir','')) 
  print "  -osdf2D  :output 2D sdf directory [%s]"%(OPT.get('osdf2D','')) 
  print "  -osdf3D  :output 3D sdf directory [%s]"%(OPT.get('osdf3D','')) 
  print "  -subdir  :use first char subdir ex) [odir] A/ATP.sdf  ('T' or 'F') [%s]"%(OPT.get('subdir','')) 
  print "  -ckcombu :full-path for ckcombu program [%s]"%(OPT.get('ckcombu',''))
  print "  -avoexist : avoid overwrite to existing 2D file (optional) [%s]"%(OPT.get('avoexist',''))
  print "  -icomp_ids :input list file for new comp_ids (optional)    [%s]"%(OPT.get('icomp_ids','')) 
  print "  -olog : output log file [%s]"%(OPT.get('olog',''))
  print "  -div  : (bunshi)/(bunbo) [%s]"%(OPT['div']);  
  print "  -A  :Action. 'T' or 'F' [%s]"%(OPT['A']);  
  sys.exit(1)

read_option(sys.argv,OPT)

if (OPT.get('olog','') != '') and (OPT.get('A','') == 'T'):
  print "#write_to_logfile --> '%s'"%(OPT['olog'])
  olog = open(OPT['olog'],'w')
  olog.write("#COMMAND %s\n"%(OPT.get('COMMAND','')))
  olog.write("#DATE    %s\n"%(OPT.get('START_DATE','')))
  for key in (OPT.keys()):
    olog.write("#OPTION '%s' '%s'\n"%(key,OPT[key]))


if (OPT.get('subdir','')=='T'):
  iciffile_list = glob.glob(OPT.get('icifdir','.') + '/*/*.cif')
else:
  iciffile_list = glob.glob(OPT.get('icifdir','.') + '/*.cif')

Nfile = len(iciffile_list)
print "#Nfile %d"%(Nfile)

if (OPT.get('icomp_ids','') != ''):
  comp_id_list = read_list_file(OPT['icomp_ids'])
  iciffile_list = select_files_by_ids(iciffile_list, comp_id_list)
  Nfile = len(iciffile_list)
  print "#Nfile_chosen %d"%(Nfile)
  #print iciffile_list

if (OPT['div'] != '0/1'):
  [bunshi,bunbo] = OPT['div'].split('/')
  bunshi = int(bunshi)
  bunbo  = int(bunbo)
  nsta = Nfile*bunshi/bunbo
  nend = Nfile*(bunshi+1)/bunbo
  print "#bunshi %d bunbo %d Nligand  %d Nsta %d Nend %d"%(bunshi,bunbo,Nfile,nsta,nend)
else:
  nsta = 0
  nend = Nfile


if (OPT.get('osdf2D','') != '') and (os.path.exists(OPT['osdf2D'])==0) and (OPT.get('A','')=='T'):
  os.mkdir(OPT['osdf2D']) 

if (OPT.get('osdf3D','') != '') and (os.path.exists(OPT['osdf3D'])==0) and (OPT.get('A','')=='T'):
  os.mkdir(OPT['osdf3D']) 


#for iciffile in (iciffile_list):
for i in range(nsta,nend):
  iciffile = iciffile_list[i]
  fields = iciffile.split('/')
  (comp_id, tail) = fields[-1].split('.')
  print "ciffile '%s' comp_id '%s'"%(iciffile,comp_id)
  if (OPT.get('osdf2D','') != ''):
    output_converted_SDF_file(iciffile,comp_id,OPT['osdf2D'],OPT.get('subdir',''),OPT.get('A',''),'2D',OPT.get('avoexist',''))
  if (OPT.get('osdf3D','') != ''):
    output_converted_SDF_file(iciffile,comp_id,OPT['osdf3D'],OPT.get('subdir',''),OPT.get('A',''),'3D',OPT.get('avoexist',''))

  if (OPT.get('olog','') != '') and (OPT.get('A','') == 'T'):
    olog.write("#%s\n"%(iciffile))


if (OPT.get('olog','') != '') and (OPT.get('A','') == 'T'):
  print "#write_to_logfile --> '%s'"%(OPT['olog'])
  olog.close()


