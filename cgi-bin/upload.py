#!/usr/bin/python

#upload milestone to USB or school server

import os, sys
import cgi, cgitb
from path import path
from activities import sftp,scp,fetchMilestonesjs
from activities import getEntries
from urllib2 import urlopen
import zipfile
import config as g
from subprocess import call, Popen, PIPE
BASE = path('/home/olpc/Activities/Learn.activity') / 'content'
log = open('/tmp/logUpload','w')

#script to update course or milestone on school server
#we must use sftp so all preparations must be done on the laptop
def do_sftp(script):
    result,err = sftp(script)
    print >> log,'do_sftp',script
    if result:
        print >> log, 'result',result
    if err:
        print >> log, 'err',err

def upload_sftp(tgt,fn):
    script = 'cd ' + tgt + '\nput ' + fn
    print >> log, 'do_sftp', script
    do_sftp(script)

def upload_it(cpth,ms):
    print >> log, 'upload_it', USB.exists(), cpth, ms
    if USB.exists():
       #copy milestone.msxo in /tmp to kls
       pth = cpth 
       src = '/tmp/' + ms + '.msxo'
       cmd = 'cp ' + src + ' ' + pth
       print >> log, cmd
       call(cmd,shell=True)
       #copy milestone.js
       src = '/tmp/milestones.js'
       cmd = 'cp ' + src + ' ' + pth
       print >> log, cmd
       call(cmd,shell=True)
    else:
        upload_sftp(tgt,fn)

def zipper(dir,zip_file):
    print >> log, 'zipper',dir,'to',zip_file
    cmd = 'rm -rf /tmp/temp'
    call(cmd,shell=True)
    cmd = 'mkdir /tmp/temp'
    call(cmd,shell=True)
    cmd = 'cp -r ' + dir + ' /tmp/temp'
    call(cmd,shell=True)
    zip = zipfile.ZipFile(zip_file,'w')
    root_len = len(os.path.abspath('/tmp/temp'))
    print >> log, 'root_len',root_len
    for root, dirs, files in os.walk('/tmp/temp'):
        archive_root = os.path.abspath(root)[root_len:]
        for f in files:
            fullpath = os.path.join(root, f)
            archive_name = os.path.join(archive_root, f)
            zip.write(fullpath, archive_name)
    zip.close()
    return zip_file


cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
ms = form.getfirst('milestone')
milestone = path(ms[:-1])
print >> log,'milestone', milestone
try:
    spth = milestone.parent
except:
    print >> log, 'parent failed',sys.exc_info()[:2] 
print >> log,'spth',spth
milestonesjs = spth / 'milestones.js'
print >> log,'milestonesjs',milestonesjs
try:
    fin=open(milestonesjs,'r')
    txt=fin.read()
    fin.close()
    milestonesjs = '/tmp/milestones.js'
    print >> log,'milestonesjs',milestonesjs
    txtout=txt.replace('blue','cyan')
    fout=open(milestonesjs,'w')
    fout.write(txtout)
    fout.close()
except:
    print >> log,'convert color failed',sys.exc_info()[:2]

#setup KLS
USB = g.USB
#copy milestone to '/tmp'
wpth = path('/tmp')
src = path(milestone)
cmd = 'cp -r '+src+' '+wpth
print >> log, 'copy milestone', cmd
try:
    pid = Popen(cmd,stdout=PIPE,stderr=PIPE,shell=True)
    result,err = pid.communicate()
    if result:
        print >> log, 'result',result
    if err:
        print >> log, 'err',err
except:
    print >> log, cmd,'failed', sys.exc_info()[:]
print >> log, 'ready to delete extraneous files'
#rm start.js lesson.css a*.txt lesson-karma.js from each activity!
delete_list = ['start.js','lesson.css','a*.txt','lesson-karma.js','index.html', 'quiz.js']
subject = milestone.parent.parent.name
course = milestone.parent.name
print >> log, subject, course, milestone.name
entries = getEntries(subject,course,milestone.name)
for entry in entries:
    for item in delete_list:
        cmd = 'rm -rf '+wpth / milestone.name / entry[4] / item
        call(cmd,shell=True)
#zip milestone to .msxo in /tmp
zipper(wpth / milestone.name, wpth / milestone.name + '.msxo')
#upload
upload_it(USB / subject / course, milestone.name)
print >> log, 'done'
log.close()
