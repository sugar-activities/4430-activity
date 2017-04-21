#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path
from activities import getFile

cgitb.enable(display=True)
log = open('/tmp/logdownload','w')
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
filename = form.getfirst('filename')
path = form.getfirst('path')
getFile(path, filename)
log.close()


