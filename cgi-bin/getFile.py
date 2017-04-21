#!/usr/bin/python
import os, sys, subprocess
import shutil
import cgi, cgitb
from BeautifulSoup import BeautifulSoup
from path import path
cgitb.enable(display=True)
log = open('/tmp/logg','w')
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
f = form.getfirst('filename', default='none given')
print >> log, 'f', f
fin = open(f, 'r')
txt = fin.read()
fin.close()
txtout = txt
soup = BeautifulSoup(txtout)
print soup.prettify()
log.close()
