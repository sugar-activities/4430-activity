#!/usr/bin/env python

import sys, time
import cgi, cgitb

log = open('/tmp/logsession','w')
cgitb.enable(display=True)
print 'Content-type:text/html\n\n'
#parameter is activity
form = cgi.FieldStorage()
activity = form.getfirst('activity', default='unknown')
print >> log, 'activity', activity
#start current_session
starttime = int(time.time())
txtout = activity + ',' + str(starttime)
print >> log, txtout
try:
    fout = open('/tmp/current_session','w')
    txt  = fout.write(txtout)
    fout.close()
except:
    print >> log,'write session record failed', sys.exc_info()[:2]
log.close()
