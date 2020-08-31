#! /software/lsstsw/stack_20200515/python/miniconda3-4.7.12/envs/lsst-scipipe/bin/python
import configargparse
from datetime import datetime, timedelta, timezone
import time
import sqlite3
import sys
import os

if len(sys.argv) < 2:
  print("mainpage.py output indir1 indir2...")
  print("output is the output directory webpage")
  print("indir are output dirs written to by observing_monitor.py")
  print("If indirs do not begin with a '/' they are assumed to be appended on output")
  sys.exit()
now = datetime.utcnow()
nowstr= now.strftime('%Y-%m-%dT%H:%M:%S')
firstnite=(now-timedelta(days=3)).strftime('%Y-%m-%d')
print(firstnite)

outdir=sys.argv[1]
outhtml=open(outdir+'/index.html','w')
outhtml.write('<html>\n<head>\n<style>\n')
outhtml.write('table, th, td {\nborder-collapse: collapse;\nfont-size: 20pt;\n }\n')
outhtml.write('p {font-size: 20pt;\n }\n')
outhtml.write('</style>\n')
outhtml.write('</head>\n<body>\n')
outhtml.write('<p>Last updated: '+nowstr+'</p>\n')
outhtml.write('<h2>Description</h2>\n')
for indir in sys.argv[2:]:
   if indir[0] != '/':
      indir = outdir+'/'+indir
   stream = indir.split('/')[-1]
   db = indir+'/observing_monitor.sqlite3'
   print(stream+' '+db)
 
outhtml.write('</body>\n</html>')
outhtml.close()

