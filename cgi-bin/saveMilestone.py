#!/usr/bin/python

#upload milestone from XO to School Server (/library/updates)

import cgi, cgitb
from activities import sftp, getMilestones, setMilestones
from path import path
import subprocess

cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
subject = form.getfirst('subject')
course = form.getfirst('course')
milestone = form.getfirst('milestone')
pth = path('content') / subject / course / milestone
log = open('/tmp/logsm','w')
print >> log, subject, course, milestone, pth
#create info.json file in folder
fin = open('/ofw/serial-number','r')
serialNumber = fin.read()
fin.close()
#get milestone entry
entries = getMilestones(subject, course)
for entry in entries:
    if milestone == entry[4]:
        info = {'subject':subject,
                'course':course,
                'milestone':milestone,
                'serial-number':serialNumber[:11],
                'entry':entry}
fout = open(pth / 'info.json','w')
fout.write(str(info))
fout.close()
#first zip the milestone in /tmp
zipf = course + milestone + '.msxo'
cmd = 'zip -r /tmp/'+ zipf + ' ' + milestone
cwd = pth.parent
print >> log, 'zip',cmd,cwd 
subprocess.call (cmd, cwd=pth.parent, shell=True)
#sftp milestone to 'updates'
script = 'cd /library/updates\nput /tmp/'+ zipf
(result, err) = sftp(script)
if result:
    print >> log, result
if err:
    print >> log, err
subprocess.call('rm -rf ' + pth / 'info.json',shell=True)
log.close()
