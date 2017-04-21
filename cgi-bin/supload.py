
#!/usr/bin/python

#upload milestone to USB or school server

import os, sys
from sugar.activity import activity
from subprocess import Popen,PIPE,call
import cgi, cgitb
from path import path
from activities import sftp,scp,fetchMilestonesjs
from activities import getEntries
from urllib2 import urlopen
import zipfile
import config as g

BASE = path(activity.get_bundle_path()) / 'content'
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

def upload_it(tgt,fn):
    if not USB.exists():
        upload_sftp(tgt,fn)
    else:
        #copy to kls
        usbtgt = USB / path(tgt).parent.name / path(tgt).name
        cmd = 'mkdir -p '+usbtgt
        print >> log, 'mkdir',cmd
        try:
            call(cmd,shell=True)
        except:
            print >> log, 'mkdir failed',sys.exc_info()[:2]
        cmd = 'cp -r ' + fn + ' ' + usbtgt
        print >> log, 'cp to KLS', cmd
        pid = Popen(cmd,stdout=PIPE,stderr=PIPE,shell=True)
        #subprocess.call(cmd, shell=True)
        result,err = pid.communicate()
        if result:
            print >> log,'cp to KLS result',result
        if err:
            print >> log,'cp to KLS err',err

def zipper(dir,zip_file):
    print >> log, 'zipper',dir,'to',zip_file
    zip = zipfile.ZipFile(zip_file,'w')
    root_len = len(os.path.abspath(dir))
    print >> log, 'root_len',root_len
    for root, dirs, files in os.walk(dir):
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
call(cmd,shell=True)

#rm start.js lesson.css a*.txt lesson-karma.js from each activity!
delete_list = ['start.js','lesson.css','a*.txt','lesson-karma.js','index.html']
subject = milestone.parent.parent.name
course = milestone.parent.name
print >> log, subject, course, milestone.name
entries = getEntries(subject,course,milestone.name)
for entry in entries:
    for item in delete_list:
        cmd = 'rm -rf '+wpth / milestone / entry[4] / item
        call(cmd,shell=True)
#zip milestone to .msxo in /tmp
cmd = 'zip -r '+milestone.name+'.msxo '+milestone.name
print >> log, 'zip milestone',cmd
call(cmd,cwd=wpth,shell=True)
sys.exit()
#upload json (milestones.js) to /library/content... and /library/lessons...
#upload milestone to /library/content...
#upload msxo to /library/lessons
#rm msxo, ms, and json from /tmp

#upload to usb if mounted, else to ss
lpth = path('/library/lessons')
cpth = path('/library/content')
ltgt = lpth / subject / course
ctgt = cpth / subject / course
#cmd = 'zip -r '+milestone+'.msxo '+milestone
#print >> log, 'zip milestone',cmd
#call(cmd,cwd=wpth,shell=True)
spth = wpth + '/' + milestone
tpth = wpth + '/' + milestone+'.msxo'
print >> log,'milestone',spth,'zip to',tpth
try:
    zippered = zipper(spth,tpth)
except:
    print >> log, 'zipper failed',sys.exc_info()[:2]
#upload msxo to lessons or kls
print >> log, 'upload_it',ltgt,zippered
upload_it(ltgt,zippered)
print >> log, 'upload milestone done'
#upload milestone.js to lessons
upload_it(ltgt,milestonesjs)
print >> log, 'upload milestones.js to lessons done'
if not USB.exists():
    #upload to /library/content
    #upload milestones.js
    upload_sftp(ctgt,milestonesjs)
    print >> log, 'upload milestones.js to content done'
    #upload milestone to cpth
    print >> log, 'scp milestone to /library/content'
    try:
        result, err =scp(wpth / milestone,ctgt)
    except:
        print >> log, 'scp failed',sys.exc_info()[:2]
    else:
        if result:
            print >> log,'scp result',result
        if err:
            print >> log,'scp err',err
    print >> log, 'upload',milestone,'done'
    #clean up /tmp (wpth)
    call('rm -rf '+spth,shell=True)
    call('rm -rf '+tpth,shell=True)
print >> log, 'done'
log.close()
