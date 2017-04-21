#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path
log=open('/tmp/logF','w')
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
subject = form.getfirst('subject')
course = form.getfirst('course')
milestone = form.getfirst('milestone',default='')
print >> log, subject, course, milestone
pth = path('content') / subject / course
if milestone:
    pth = pth / milestone
folders=pth.dirs()
print >> log,pth,len(folders),folders
done = False
n=1
while not done:
    number = str(n)
    if len(number)<2:
        number = '0'+number
    if milestone:
        folder = 'a'+number
    else:
       folder = 'ms'+number
    fpth = pth / folder
    if fpth.exists():
        n += 1
    else:
        done = True
print >> log, folder
log.close()
print folder
