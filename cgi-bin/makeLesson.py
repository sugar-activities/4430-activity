#!/usr/bin/python
import sys, subprocess
import cgi, cgitb
from buildLesson import buildLesson

cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
log = open('/tmp/logb','w')
form = cgi.FieldStorage()
pth = form.getfirst('activity', default="")
buildLesson(pth)

