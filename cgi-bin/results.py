#!/usr/bin/env python

import sys, subprocess, time
import cgi, cgitb
from sugar.activity import activity
from sugar.datastore import datastore
from path import path
from activities import getEntries
from activities import setEntries

log = open('/tmp/logApply','w')
cgitb.enable(display=True)
print 'Content-type:text/html\n\n'
#parameter are score, subject, milestone, activity
form = cgi.FieldStorage()
score = form.getfirst('score')
subject = form.getfirst('subject')
course = form.getfirst('course')
milestone = form.getfirst('milestone')
learn_activity = form.getfirst('activity')
start = form.getfirst('start')
stop = form.getfirst('stop')
detail = form.getfirst('detail',default='')
print >> log, 'score', score
print >> log, 'subject', subject 
print >> log, 'course', course 
print >> log, 'milestone', milestone
print >> log, 'activity', learn_activity
print >> log, 'start', start
print >> log, 'stop', stop
print >> log, 'detail', detail
#create datastore entry
datastore_entry = datastore.create()
datastore_entry.metadata['title']='attempt'
datastore_entry.metadata['title_set_by_user'] = 1
datastore_entry.metadata['keep'] = 0

#build attempt json
attempt = {}
attempt['start'] = start
attempt['stop'] = stop
attempt['result'] = score
attempt['subject'] = subject
attempt['course'] = course
attempt['milestone'] = milestone
attempt['activity'] = learn_activity
attempt['detail'] = detail
#create datastore entry
datastore_entry = datastore.create()
datastore_entry.metadata['activity'] = 'rw.olpc.Learn'
datastore_entry.metadata['title']='attempt'
datastore_entry.metadata['title_set_by_user'] = 1
datastore_entry.metadata['keep'] = 0
datastore_entry.metadata['attempt'] = str(attempt)
datastore.write(datastore_entry)
#tell activity what to do next:
retval = 9
if int(score) < 70:
    retval = 0
else: 
    entries = getEntries(subject, course, milestone)
    for i in range(len(entries)):
        if entries[i][4] == learn_activity:
            entries[i][5] = 'green'
            if i + 1 < len(entries):
                entries[i+1][5] = 'yellow'
                retval = 0
                setEntries(subject, course, milestone,entries)
                break
            else: #done with this milestone
                entries = getEntries(subject,course,'')
                for j in range(len(entries)):
                    if entries[j][4] == milestone:
                        entries[j][5] = 'green'
                        if j + 1 < len(entries):
                            entries[j+1][5] = 'yellow'
                            retval = 1
                            setEntries(subject,course,'',entries)
                        else: #done with the course!!!
                            retval = 1
                        break
        else:
            print >> log, learn_activity, i, entries[i][4]
print retval
print >> log, 'retval',retval
log.close()
