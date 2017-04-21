#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path
from activities import getFile

log = open('/tmp/logsetup','w')
basepth = path('content')
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
pth = basepth / 'subjects.js'
fin = open(pth,'r')
txt = fin.read()
fin.close()
lines = txt.split('\n')
for line in lines:
    try:
        entry = eval(line)[0]
    except:
        continue
    if len(entry)<3:
        entry = eval(line)
    print >> log, line, len(entry)
    print >> log, entry[0],entry[1],entry[2]
    subject = entry[1]
    srcpth = path(subject)
    tgtpth = basepth / subject
    if not tgtpth.exists():
        subprocess.call('mkdir ' + tgtpth,shell=True)
        result = getFile(srcpth, '*.js')
        result = getFile(srcpth, '*.html')
        result = getFile(srcpth, '*.png')
        result = getFile(srcpth, '*.gif')
        print >> log, 'loaded',srcpth
print >> log, 'done'
log.close()
