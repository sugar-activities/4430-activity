#!/usr/bin/python
import os, sys
from subprocess import Popen,PIPE,call
import cgi, cgitb
from path import path

log = open('/tmp/logCopy','w')
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
   #copy milestone to /tmp
   dst = BASE / 'mscopy'
   src = path('content/') / subject / course / milestone
   call('rm -rf ' + dst,shell=True)
   call('mkdir ' + dst,shell=True)
   call('cp -r ' + src + ' ' + dst,shell=True) 
else:
   #copy activity to /tmp
   dst = BASE / 'actcopy'
   src = path('content') / subject / course / milestone / activity 
   call('rm -rf ' + dst,shell=True)
   call('mkdir ' + dst,shell=True)
   call('cp -r ' + src + ' ' + dst,shell=True)
print >> log, 'done'
log.close()
