#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path
cgitb.enable(display=True)
log = open('/tmp/logExists','w')
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
f = form.getfirst('filename', default='none given')
print >> log, 'f', f
if path(f).exists():
    print 'true'
else:
    print 'false'
log.close()
