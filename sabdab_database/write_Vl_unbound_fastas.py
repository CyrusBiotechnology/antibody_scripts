#!/usr/bin/python

import os,sys
import fileinput
import urllib2
from collections import defaultdict

if len(sys.argv) > 1:
  infile = sys.argv[1]
else:
  infile = 'unbound_2.0.csv'

d = defaultdict(list)

for line in fileinput.input(infile):
  if line.startswith('pdb'): continue
  else:
    # filter out nanobodies and single-chain Fabs
    if (line.rsplit()[2] == 'NA') or (line.rsplit()[1] == 'NA'): continue
    else:
			# get chain ID of chain we want, [1]=Vh, [2]=Vl
#      d[line.rsplit()[0]].append(line.rsplit()[1])
      d[line.rsplit()[0]].append(line.rsplit()[2])

print '\nmaking Fl fasta files for %i unbound Fab structures'%(len(d))
print infile.rsplit('_')[1][:-4]
#fout = open('unbound_%s/%s_Fl'%(infile.rsplit('_')[:-4]),'w')
for key in d:
#  print key
  fasta_list = []
  # get fasta sequences for specified light chains
  command = 'https://www.rcsb.org/pdb/download/viewFastaFiles.do?structureIdList=%s&compressionType=uncompressed'%(key) 
  response = urllib2.urlopen(command)
  fasta = response.read().rsplit('\n')
  for x in range(len(fasta)):
    if fasta[x].startswith('>'):
      if fasta[x].rsplit(':')[1][0] in d[key]:
        fasta_1 = ''
        newpdb = False; ii = 0
        while not newpdb:
          ii += 1
          if not ((fasta[x+ii].startswith('>')) or (x+ii == len(fasta)-1)):
            fasta_1 += fasta[x+ii].rsplit()[0]
          else:
            newpdb = True
        fasta_list.append(fasta_1)
  if len(d[key]) > 1:
    if len(set(fasta_list)) > 1:
      print key, d[key]
      if len(set(fasta_list)) != len(d[key]):
        sys.exit('number of unique light chain sequences not equal to the number of total light chains in %s'%(key))
      else:
        for x in range(len(fasta_list)):
          fname = 'unbound_%s/light/%s_%s_Fl.fasta'%(infile.rsplit('_')[1][:-4],key,d[key][x])
          if not os.path.exists(os.path.dirname(fname)):
	          os.makedirs(os.path.dirname(fname))
          fout = open( fname, 'w' )
          fout.write('>%s_%s\n'%(key,d[key][x]))
          fout.write('%s\n'%(fasta_list[x]))
          fout.close()
  else:
    fname = 'unbound_%s/light/%s_%s_Fl.fasta'%(infile.rsplit('_')[1][:-4],key,d[key][0])
    if not os.path.exists(os.path.dirname(fname)):
      os.makedirs(os.path.dirname(fname))
    fout = open( fname, 'w' )
    fout.write('>%s_%s\n'%(key,d[key][0]))
    fout.write('%s\n'%(fasta_list[0]))
    fout.close()

