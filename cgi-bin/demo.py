#!/usr/bin/python
import os, sys, traceback, subprocess
import cgi, cgitb
from path import path
from sugar.activity import activity
from activities import setRole

BASE = path(activity.get_bundle_path()+'/content')
roles = {'staff':'p4','p4':'p5','p5':'p6','p6':'staff'}

cgitb.enable(display=True)
log = open('/tmp/logDemo','w')
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
inrole = form.getfirst('role', default='staff')
try:
    role = roles[inrole]
except:
    print >> log, 'key error', sys.exc_info()[:2],
    #print >> log, traceback(sys.exc_info()[3]
    role = ''
else:
    print role
    print >> log, 'role', inrole, role
setRole(role)
fin=open(BASE / 'subjects.js')
txt=fin.read()
fin.close()
txtout = ''
lines = txt.split('\n')
for line in lines:
    if 'role' in line:
        txtout += "var role = '"+role+"';\n"
    else:
        txtout += line + '\n'
fout=open(BASE / 'subjects.js','w')
fout.write(txtout)
fout.close()
log.close()
