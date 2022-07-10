#!/usr/bin/env python
import sys
import os
from datetime import datetime
import time

LastModDate = "July 31, 2013"


def read_option(argv,opt_dic):
  opt_dic['COMMAND'] = argv[0]
  now = datetime.now()
  opt_dic['START_DATE'] = now.strftime("%Y/%m/%d %H:%M:%S")

  for i in range(1,len(argv)):
    opt_dic['COMMAND'] += ' '
    opt_dic['COMMAND'] += argv[i]
    if (argv[i][0]=='-'):
      if ((i+1)<len(argv)):
        if (argv[i+1][0]!='-'):
          opt_dic[argv[i][1:]] = argv[i+1]


def read_list_file(ifname,list):
  print "#read_list_file('%s')"%(ifname)
  if not os.access(ifname,os.R_OK):
    print "#ERROR:Can't open filename '%s'" %(ifname)
    return(0)
  f = open(ifname)
  for line in f:
    line = line.rstrip('\n')
    if (line.startswith('#')==0):
     #print line
     fields = line.split()
     list.append(fields[0])
  f.close()


def read_multi_sdf_file_and_write_the_last(ifname,ofname):
  print "#read_multi_sdf_file_and_write_the_last('%s')-->'%s'"%(ifname,ofname)
  
  ### [1] read ifname ##
  if (os.access(ifname,os.R_OK)==0):
    return('')
  f = open(ifname)
  lines = []
  Nline_ddd = [] 
  for line in f:
    lines.append(line)
    if (line.startswith('$$$')):
      Nline_ddd.append(len(lines)-1)
  f.close()

  Nline_end = Nline_ddd[-1]
  if (len(Nline_ddd)>1):
    Nline_sta = Nline_ddd[-1-1] + 1
  else:
    Nline_sta = 0

  ### [2] output ofname ##
  of = open(ofname,"w")
  for i in range(Nline_sta,Nline_end+1):
    of.write("%s"%(lines[i]))
  of.close()

def Action(comstr,action):
  if (action=='T'):
    os.system(comstr)
  else:
    print "#%s"%(comstr)


def add_comp_time_to_pdb(ifname,comp_time):
  print "#add_comp_time_to_pdb('%s',comp_time)"%(ifname)
  lines = []
  if (os.access(ifname,os.R_OK)==0):
    print "#WARNING(add_comp_time_to_pdb):Can't open '%s'."%(ifname)
    return(0)
  f = open(ifname)
  for line in f:
    lines.append(line)
  f.close() 
  of = open(ifname,'w')
  #REMARK COMP_TIME  3.891029 seconds
  of.write("REMARK COMP_TIME  %f seconds\n"%(comp_time))
  for line in lines:
    of.write("%s"%(line))
  of.close() 
  return(1)


############
### MAIN ###
############

OPT = {}
OPT['L']   = 'ligand.list'
OPT['idref'] = 'MOL2_SupLIG'

OPT['A'] = 'F'
OPT['div'] = '0/1'
OPT['idmol2'] = ''
OPT['idsdf']  = ''


OPT['odtar'] = 'tmpout'
OPT['chpdb'] = 'T'

OPT['avex'] = 'F'
OPT['self'] = 'F'
OPT['aevo'] = 'I' 


if (len(sys.argv)<2):
  print "mk_shaep.py <options>"
  print " for making simimilariy-based 3D model using 'shaep' program."
  print " coded by T.Kawabata. LastModified:%s"%(LastModDate)
  print "<usages>"
  print "mk_shaep.py -L [list_of_ligands] -idsdf  [dir_for_ideal_target(SDF_3D_BALLOON)] -odtar [SHAEP]"
  print "mk_shaep.py -L [list_of_ligands] -idmol2 [dir_for_ideal_target(MOL2_3D_BALLOON)] -odtar [SHAEP]"
  print "<options>"
  print " -L      : list of library molecules[%s]"%(OPT['L'])
  print " -idref  : input  dir for reference template molecules[%s]"%(OPT['idref'])
  print " -idsdf  : input  dir for target 3D SDF  molecules[%s]"%(OPT['idsdf'])
  print " -idmol2 : input  dir for target 3D MOL2 molecules[%s]"%(OPT['idmol2'])
  print " -odtar  : output dir for predicted (transformed) target molecule[%s]"%(OPT['odtar'])
  print " -chpdb  : Change the best sdf model into PDB format (T or F) [%s]"%(OPT['chpdb'])
  print " -div    : Job division (bunshi/bunbo) [%s]"%(OPT['div'])
  print " -A      : Action (T or F) [%s]"%(OPT['A'])
  print " -avex   : avoid existing file pairs in '-odtar' (T or F)[%s]"%(OPT['avex'])
  print " -self   : only self modeling (T or F)[%s]"%(OPT['self'])
  sys.exit(1)


### [1] read option ###
read_option(sys.argv,OPT)
[bunshi,bunbo] = OPT['div'].split('/')
bunshi = int(bunshi)
bunbo  = int(bunbo)

### [2] read liglist (-L) ###
liglist = []
read_list_file(OPT['L'],liglist)

Nlig  = len(liglist)

### [3] count Npair ###
Npair = 0
for ligTAR in (liglist):   ## target ##
  fieldTAR = ligTAR.split('_')
  ligname3TAR = fieldTAR[0]
  #(ligname3TAR,pdbchTAR) = ligTAR.split('_')
  for ligREF in (liglist): ## template ##
    fieldREF = ligREF.split('_')
    ligname3REF = fieldREF[0]
    (ligfilecoreREF,tail) = ligREF.split('.')
    #(ligname3REF,pdbchTMP) = ligREF.split('_')
    reference_file = "%s/%s_%s.pdb"%(OPT['odtar'],ligname3TAR,ligREF)
    if ((OPT['self']!='T') or (ligTAR == ligREF)) and ((OPT['avex']=='F') or (os.access(reference_file,os.R_OK)==0)):
      Npair += 1

#Npair = Nlig * Nlig

Nsta = Npair*bunshi/bunbo
Nend = (Npair*(bunshi+1))/bunbo
print "#Nlig %d Npair %d bunshi %d bunbo %d Nsta %d Nend %d"%(Nlig,Npair,bunshi,bunbo,Nsta,Nend)
npair = 0

### [4] do ShaEP ###
  
for ligTAR in (liglist):   ## target ##
  fieldTAR = ligTAR.split('_')
  ligname3TAR = fieldTAR[0]
  #(ligname3TAR,pdbchTAR) = ligTAR.split('_')
  #print "%s '%s' '%s'"%(ligTAR,ligname3TAR,pdbchTAR)
  for ligREF in (liglist): ## template ##
    (headREF,tailREF) = ligREF.split('.')
    fieldREF = headREF.split('_')
    ligname3REF = fieldREF[0]
    (ligfilecoreREF,tail) = ligREF.split('.')
    #(ligname3REF,pdbchTMP) = ligREF.split('_')
    #print "%s '%s' '%s'"%(ligREF,ligname3REF,pdbchTMP)
    reference_file  = "%s/%s.mol2"%(OPT['idref'],ligfilecoreREF)

    if (OPT['idmol2'] != ''):
      itarget_file    = "%s/%s.mol2"%(OPT['idmol2'],ligname3TAR)
    if (OPT['idsdf']  != ''):
      itarget_file    = "%s/%s.sdf"%(OPT['idsdf'],ligname3TAR)

    moutsdffile = "%s/%s_%s.msdf"%(OPT['odtar'],ligname3TAR,headREF)
    outsdffile  = "%s/%s_%s.sdf"%(OPT['odtar'],ligname3TAR,headREF)
    outpdbfile  = "%s/%s_%s.pdb"%(OPT['odtar'],ligname3TAR,headREF)
    outsimfile  = "%s/%s_%s_hits.txt"%(OPT['odtar'],ligname3TAR,headREF)
    outsimhead  = "%s/%s_%s"%(OPT['odtar'],ligname3TAR,headREF)

    if ((OPT['self']!='T') or (ligTAR == ligREF)) and ((OPT['avex']=='F') or (os.access(outpdbfile,os.R_OK)==0)):
      if (Nsta<=npair) and (npair<Nend):

        if (os.path.exists(reference_file)==0):
          print "#WARNING:reference_file '%s' does not exist."%(reference_file)
          reference_file = reference_file + '.mol2'
          if (os.path.exists(reference_file)):
            print "#change reference_file into '%s'."%(reference_file)
          else:
            print "#ERROR:reference_file '%s' does not exist."%(reference_file)
            sys.exit(1)

        if (os.path.exists(itarget_file)==0):
          print "#WARNING:itarget_file '%s' does not exist."%(itarget_file)
          if (os.path.exists(itarget_file)):
            print "#change itarget_file into '%s'."%(itarget_file)

 
        if (os.path.exists(moutsdffile)):
          comstr = "rm %s"%(moutsdffile)
          Action(comstr,OPT['A'])

        if (os.path.exists(outsimfile)):
          comstr = "rm %s"%(outsimfile)
          Action(comstr,OPT['A'])

        if (os.path.exists(outsimhead)):
          comstr = "rm %s"%(outsimhead)
          Action(comstr,OPT['A'])

        sta_sec = time.time()
#        comstr = "shaep  %s %s --output-file %s --nStructures 0 -s %s"%(reference_file,itarget_file,outsimhead,moutsdffile)
        comstr = "shaep  -q %s %s --output-file %s --nStructures 1 -s %s"%(reference_file,itarget_file,outsimhead,outsdffile)
        Action(comstr,OPT['A'])
        end_sec = time.time()

#        if (OPT['A']=='T'):
#          read_multi_sdf_file_and_write_the_last(moutsdffile,outsdffile)

        if (OPT['chpdb']=='T'): 
          delta_sec = end_sec - sta_sec 
          comstr_babel = "babel -isdf %s -opdb %s"%(outsdffile,outpdbfile)
          Action(comstr_babel,OPT['A']) 
          if (OPT['A']=='T'):
            add_comp_time_to_pdb(outpdbfile,delta_sec)
          else:
            print "#add_comp_time_to_pdb(outpdbfile,delta_sec:%f)"%(delta_sec)

      npair += 1 
