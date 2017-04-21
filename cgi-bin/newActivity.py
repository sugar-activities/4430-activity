#!/usr/bin/python

#generate new basic activity

import cgi, cgitb
from activities import getEntries, setEntries
from path import path
import subprocess

cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
subject = form.getfirst('subject')
course = form.getfirst('course')
milestone = form.getfirst('milestone')
activities = getEntries(subject, course, milestone)
log = open('/tmp/logna','w')
print >> log, subject, course, milestone, len(activities)
log.close()
#add entry for new milestone
n = str(len(activities)+1)
n2 = n
if len(n2) < 2:
    n2 = '0' + n
name = 'a' + n2
newentry = []
newentry.append(n)
newentry.append(n)
newentry.append(course)
newentry.append('basic')
newentry.append(name)
newentry.append('blue')
newentry.append("activity " + n2)
activities.append(newentry)
setEntries(subject, course, milestone, activities)
#create folder
pth = path('content') / subject / course / milestone / name
cmd = 'mkdir ' + pth
subprocess.call(cmd,shell=True)
cmd = 'cp cgi-bin/activities/index.html ' + pth
subprocess.call(cmd,shell=True)
cmd = 'cp cgi-bin/activities/source.txt ' + pth
subprocess.call(cmd,shell=True)
