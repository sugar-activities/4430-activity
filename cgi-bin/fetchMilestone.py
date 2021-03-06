#!/usr/bin/python
#
#in staff mode, downloads one specified milestone
#in student mode, checks milestones.js to determine which milestones are local
#downloads additional milestones until there is current (yellow) milestone + 1
#erases completed milestones until there are a max of three milestones local
log=open('/tmp/loge','w')

import os, sys, subprocess
try:
    import cgi, cgitb
    from path import path
    import config as g
    from activities import fetchMilestone
    from activities import getEntries
    from activities import setEntries
except:
    print >> log, 'import failed', sys.exc_info()[:2]
log.close()

def fetch(subject, course, milestone):
    print >> log,'fetch',subject,course,milestone
    try:
        result = fetchMilestone(subject, course, milestone)
        print >> log, 'fetchMilestone', result
    except:
	print >> log, 'fetchMilestone failed', sys.exc_info()[:2]
        result = 1
    return result

def remove(subject, course, milestone):
    cmd = 'rm -rf ' + path('content') / subject / course / milestone
    subprocess.call(cmd, shell=True)
    
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
log = open('/tmp/logFetch','w')
try:
    form = cgi.FieldStorage()
    print >> log, 'form', form
except:
    print >> log, 'form failed', sys.exc_info()[:2]
milestone = form.getfirst('milestone')
subject = form.getfirst('subject')
course = form.getfirst('course').replace('\n','')
course_type = form.getfirst('course_type')
enrollment = form.getfirst('enrollment')
role = g.role
try:
    entries = getEntries(subject, course, '')
except:
    print >> log,'getEntries failed',sys.exc_info()[:2]
else:
    print >> log,'getEntries succeeded',len(entries)
yellow = ''

print >> log, 'role', role,'enrollment', enrollment,'course_type', course_type
if role == 'staff' or enrollment == 'open' or course_type == 'U':
    print >> log, 'fetch',subject,course,milestone,role,enrollment
    result = fetch(subject, course, milestone)
    if result == 0:
        for entry in entries:
            ms = entry[4]
            if ms == milestone:
                entry[5] = 'blue'
else: #it is a student
    print >> log,'it is a student',role
    ms = 0
    for entry in entries:
        if entry[5] == 'yellow':
            ms += 1
    if ms < 1:
        #download first milestone and make current
        milestone = entries[0][4]
        result = fetch(subject, course, milestone)
        if result == 0:
            entries[0][5] = 'yellow'
            aentries = getEntries(subject, course, milestone)
            aentries[0][5] = 'yellow'
            setEntries(subject,course, milestone, aentries)
    ms = 0
    for entry in entries:
         if entry[5] == 'blue':
            ms += 1
    if ms < 1:
         #download first cyan milestone
         for i in range(len(entries)):
              if entries[i][5] == 'cyan':
                   result = fetch(subject, course, entries[i][4])
                   if result == 1:
                       entries[i][5] = 'blue'
                   break
    ms = 0
    for entry in entries:
         if entry[5] == 'green' or entry[5] == 'yellow' or entry[5] == 'blue':
             ms += 1
    while ms > 3:
         for i in range(len(entries)):
             if entries[i][5] == 'green':
                 remove(entries[i])
                 entries[i][5] = 'chartreuse'
                 ms -= 1

newentries = []
for entry in entries:
    newentries.append(entry)
    try:
        setEntries(subject, course, '', newentries)
    except:
	print >> log, 'setEntries failed', subject, course, sys.exc_info()[:2]

if yellow:
    getEntries(subject, course, yellow)
    entries[0][5] = 'yellow'
    setEntries(subject,course, yellow, entries)
log.close()
