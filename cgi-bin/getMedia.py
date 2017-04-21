#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path
cgitb.enable(display=True)
print 'Content-Type:audio/ogg\n\n'
form = cgi.FieldStorage()
f = form.getfirst('filename', default='none given')
fin=open(f,'r')
clip = fin.read()
fin.close()
print clip
