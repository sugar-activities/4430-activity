#!/usr/bin/python
import os, sys
from subprocess import Popen,PIPE,call
import cgi, cgitb
from path import path

log = open('/tmp/logPaste','w')
BASE = path('/tmp')

cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
subject = form.getfirst('subject')
course = form.getfirst('course')
milestone = form.getfirst('milestone')
activity = form.getfirst('activity')
print >> log,'form',subject,course,milestone,activity
if not activity:
   src = BASE / 'mscopy'
   dst = path('content/') / subject / course / milestone
   call('cp -r ' + src + ' ' + dst,shell=True) 
else:
   src = BASE / 'actcopy'
   dst = path('content') / subject / course / milestone / activity 
   call('cp -r ' + src + ' ' + dst,shell=True)
print >> log, 'done'
log.close()
