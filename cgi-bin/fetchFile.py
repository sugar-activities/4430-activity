#!/usr/bin/python
import os, sys, subprocess
import shutil
import cgi, cgitb
from BeautifulSoup import BeautifulSoup
from path import path
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
log = open('/tmp/logFetchFile','w')
form = cgi.FieldStorage()
print >> log, 'form', form
f = form.getfirst('openfile', default='none given')
fpth = path(f)
print >> log, 'f=', fpth
srcpth = fpth.parent
print >> log, 'srcpth=', srcpth
fullpth = srcpth / 'source.txt' 
print >> log, 'fullpth=',fullpth
if fullpth.exists():
    fin = open(fullpth, 'r')
    txt = fin.read()
    fin.close()
    #make comments visible as text
    comment = False
    pre = False
    needpre = False
    lines = txt.split('\n')
    for line in lines:
        if comment:
            if '-->' in line:
                line = line.replace('-->','*/')
                comment = False
            print line
            if needpre:
                needpre = False
                print '</pre>'
        elif '<!--' in line:
            line = line.replace('<!--',"/*")
            if '-->' in line:
                line = line.replace('-->',"*/")
            else:
                comment = True
                if '/*Quiz' in line:
                    if not pre:
                        print '<pre>'
                        pre = True
                        needpre = True
            print line
        elif '<pre>' in line:
            pre = True
            print line
        else:
            print line                
    print >> log, 'done'
else:
    print >> log, 'no source file'
    print ' '
log.close()
