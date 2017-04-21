#!/usr/bin/python

#generate new empty milestone

import cgi, cgitb
from activities import getMilestones, setMilestones
from path import path
import subprocess

cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
subject = form.getfirst('subject')
course = form.getfirst('course')
milestones = getMilestones(subject, course)
log = open('/tmp/lognm','w')
print >> log, subject, course, len(milestones)
log.close()
#add entry for new milestone
n = str(len(milestones)+1)
n2 = n
if len(n2) < 2:
    n2 = '0' + n2
name = 'ms' + str(n2)
newentry = []
newentry.append('0')
newentry.append(n)
newentry.append('sj')
newentry.append('milestone')
newentry.append(name)
newentry.append('blue')
newentry.append("milestone " + n2)
milestones.append(newentry)
setMilestones(subject, course, milestones)
#create folder
pth = path('content') / subject / course / name
cmd = 'mkdir ' + pth
subprocess.call(cmd,shell=True)
cmd = 'cp cgi-bin/templates/index.html ' + pth
subprocess.call(cmd,shell=True)
cmd = 'cp cgi-bin/templates/activities.js ' + pth
subprocess.call(cmd,shell=True)
