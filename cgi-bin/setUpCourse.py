#!/usr/bin/python
import os, sys, subprocess, traceback
import cgi, cgitb
from path import path
from activities import getFile
from activities import getRole
from buildMenu import buildMenu

basepth = path('content')
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
subject = form.getfirst('subject')
log = open('/tmp/logcourse','w')
print >> log, 'subject',subject
try:
    role = getRole()
except:
    print >> log,'getRole failed',sys.exc_info()[:2]
    print >> log, traceback(sys.exc_info()[3])
else:
    print >> log, 'getrole succeeded',role
pth = basepth / subject / 'courses.js'
fin = open(pth,'r')
txt = fin.read()
fin.close()
lines = txt.split('\n')
for line in lines:
    try:
        entry = eval(line)[0]
    except:
        continue
    if len(entry) < 3:
        entry = eval(line)
    course = entry[0].lower()
    course_type=entry[1][0]
    if course_type == 'U':
        enrollment = entry[1][1:]
    elif course_type == 'M':
        enrollment = entry[1][1:]
    else:
        enrollment = entry[1]
    print >> log, 'course_type', course_type, 'enrollment',enrollment
    pth = path(subject) / course
    tgtpth = basepth / pth
    print >> log, 'tgtpth', tgtpth, enrollment
    if role == 'staff' or enrollment == role or enrollment == 'open':
        if not tgtpth.exists():
            print >> log, 'making directory',tgtpth
            subprocess.call('mkdir ' + tgtpth,shell=True)
            result = getFile(pth, 'milestones.js')
            if result:
                print >> log,'get Milestone',result
            #make index.html
            result = buildMenu('unit')
            fout = open(tgtpth / 'index.html','w')
            fout.write(result)
            fout.close()
            pth = path(subject) / entry[2]
            print >> log, 'getting',pth.parent,pth.name
            result = getFile(pth.parent,pth.name)
            print >> log, 'loaded',tgtpth
        this_course = course
response = this_course + ',' + role + ',' + course_type + ','
print >> log, 'response = ',response
print response
print >> log, 'done'
log.close()
