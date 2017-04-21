#!/usr/bin/python
import os, sys, traceback
from subprocess import Popen,PIPE,call
from path import path
from urllib2 import urlopen
from buildLesson import buildLesson
from buildMenu import buildMenu

import config as g
g.using_gconf = True

DATAPATH = path('/tmp')
WORKPATH = DATAPATH / 'work'
call('mkdir -p ' + WORKPATH,shell=True)
g.USB = path('')
if path('/run/media/olpc/').exists():
    usbpath = path('/run/media/olpc')
else:
    usbpath = path('/media')
usbdrives = path(usbpath).dirs()
for usbdrive in usbdrives:
    g.USB = usbdrive / 'kls'
    if g.USB.exists():
        break
g.SS = path('/library/lessons')
target = path('/home/olpc/Activities/Learn.activity')
config_pth = path('~/.sugar/default/config')

def scp(src,dst):
    authpth = '~/.sugar/default/owner.key'
    auth = ' -oIdentityFile=' + authpth
    srvr = g.serial_number + '@schoolserver:'+dst
    cmd = 'scp -r ' + auth + ' ' +src+' '+ srvr
    pipe1 = 'stdout=PIPE'
    pipe2 = 'stderr=PIPE'
    pid = Popen(cmd,stdout=PIPE,stderr=PIPE,shell=True)
    (result,err) = pid.communicate()
    return result, err
    
#executes sftp command contained in scrpt
#note script must be written to disk and read by sftp command
def sftp(script, folder = None):
    pth = WORKPATH / 'script'
    call('rm -rf ' + pth, shell=True)
    call('mkdir -p ' + WORKPATH, shell=True)
    fout = open(pth, 'w')
    fout.write(script)
    fout.close()
    authpth = '/home/olpc/.sugar/default/owner.key'
    auth = ' -oIdentityFile=' + authpth
    scrpt = ' -b ' + pth
    srvr =  g.serial_number + '@schoolserver'
    cmd = 'sftp ' + auth + scrpt + ' ' + srvr
    log = open('/tmp/logSFTP','w')
    print >> log, 'sftp', cmd
    log.close()
    pipe1 = 'stdout=PIPE'
    pipe2 = 'stderr=PIPE'
    if folder:
        pid = Popen(
            cmd, 
            stdout=PIPE,
            stderr=PIPE,
            cwd=folder, 
            shell=True)
    else:
        pid = Popen(
            cmd, 
            stdout=PIPE,  
            stderr=PIPE, 
            shell=True)
    (result,err) = pid.communicate()
    return result, err

def isConnected():
    try:
        connected = 'true'
        ret = urlopen('http://schoolserver/')
    except:
        connected = 'false'
    return connected

def getInstalled(subject):
    pth = path('content') / subject
    temp = pth.dirs()
    milestones = []
    for item in temp:
        milestones.append(str(item.namebase))
    milestones.remove('karma')
    return milestones

def extractEntries(txt):
    lines = txt.split(';')
    line = lines[0].replace('\n',' ')
    pos = line.find('=')
    line = line[pos+1:]
    entries = eval(line)
    return entries

def getEntries(subject, course, milestone,super=''):
    if super:
        pth = path('content') / super / subject
    else:
        pth = path('content') /subject
    if len(milestone) > 0:
        fpth = pth / course / milestone / 'activities.js'
    else:
        fpth = pth / course / 'milestones.js'
    fin = open(fpth,'r')
    txt = fin.read()
    fin.close()
    return extractEntries(txt)

def setEntries(subject, course, milestone, entries,super=''):
    log = open('/tmp/logSet','w')
    if super: 
       	pth = path('content') /	super /	subject
    else:
        pth = path('content') /subject
    if len(milestone) > 0:
        fpth = pth / course / milestone / 'activities.js'
    else:
        fpth = pth / course / 'milestones.js'
    txtout = 'var activities = [\n'
    for entry in  entries:
        txtout = txtout + str(entry) + ',\n' 
    txtout = txtout + '];\n'
    print >> log, 'txtout',txtout
    print >> log, 'fpth',fpth
    try:
        fout = open(fpth,'w')
        fout.write(txtout)
        fout.close()
    except:
        print >> log, 'write failed',sys.exc_info[:2]
    log.close()

def getMilestones(subject, course):
    milestones = getEntries(subject,course, "")
    return milestones

def getActivities(subject, milestone):
    activities = getEntries(subject, 0, milestone)
    return activities

def setMilestones(subject, course, milestones):
    setEntries(subject,course, "", milestones)

def setActivities(subject, milestone, activities):
    setEntries(subject, 0, milestone, activities)

def fetchMilestonesjs(subject,course):
    log = open('/tmp/logJSfetch','w')
    folder = path('/tmp')
    if g.USB.exists(): #get from usb drive
        src = g.USB / subject / course / 'milestones.js'
        cmd = 'cp -r ' + src + ' ' + folder
        call(cmd,shell=True)
    else: #get from schoolserver
        pth = g.SS / subject / course
        script = 'cd ' + str(pth) + '\nget ' + 'milestones.js'
        (result,err) = sftp(script, folder)
        if result:
            print >> log, 'sftp result',result
        if err:
            print >> log, 'sftp err',err
    fin=open('/tmp/milestones.js','r')
    js=fin.read()
    fin.close()
    print >> log,'js',js
    log.close()
    return js

def fetchMilestone(subject, course, milestone):
    log = open('/tmp/logAfetch','w')
    print >> log,'fetchMilestone in activities.py',subject, course, milestone
    if g.USB.exists(): #get from usb drive
        try:
            print >> log,'fetch from usb', g.USB
            src = g.USB / subject / course / milestone + '.msxo'
            dst = path('content') / subject / course
            cmd = 'cp -r ' + src + ' ' + dst
            print >> log,'cmd',cmd
            call(cmd,shell=True)
        except:
            print >> log, 'usb failed', sys.exc_info()[:2]
    else: #get from schoolserver
        try:
            folder = path('content') / subject / course
            pth = g.SS / subject / course
            script = 'cd ' + str(pth) + '\nget ' + milestone + '.msxo'
            print >> log, script
        except:
            print >> log, 'script failed', sys.exc_info()[:2]
        (result,err) = sftp(script, folder)
        if result:
            print >> log, 'sftp result',result
        if err:
            print >> log, 'sftp err',err
    try:
        bndl = milestone + '.msxo'
        cwd = path('content') / subject / course
        pth = cwd / bndl
        if pth.exists():
            cmd = 'unzip ' + bndl
            call(cmd,cwd=cwd,shell=True)
            cmd = 'rm -rf ' + bndl
            call(cmd, shell=True)
            #here we need to build index.html
            result = buildMenu('lesson')
            fout = open(cwd / milestone / 'index.html','w')
            fout.write(result)
            fout.close()
            #here we need to build the lessons
            entries = getEntries(subject,course,milestone)
            for entry in entries:
                try:
                    lessonPth = cwd / milestone / entry[4]
                    addl,adds  = buildLesson(lessonPth)
                except:
                    print >> log,'buildLesson failed',lessonPth,sys.exc_info()[:2]
                try:
                    result = buildMenu('activity',added_links=addl,added_scripts=adds)
                except:
                    print >> log,'buildMenu failed',addl,added,sys.exc_info()[:2]
                try:
                    fout = open(cwd / milestone / entry[4] / 'index.html','w')
                    fout.write(result)
                    fout.close()
                except:
                    print >> log,'write failed',entry[4],sys.exc_info()[:2]
            log.close()
            return 0
        else:
            print >> log, 'no milestone available',pth
            log.close()
            return 1
    except:
        print >> log, 'bndl processing failed',sys.exc_info()[:2]
        log.close()

def getActivitiesJs(subject):
    if g.USB.exists(): #get from usb drive
        pth = g.USB / subject
        cmd = 'cp -r ' + pth / 'activities*' + ' ' + 'content/'+ subject
        call(cmd,shell=True)
    else: #get from schoolserver
        folder = 'content/'+ subject
        pth = g.SS / subject
        script = 'cd ' + str(pth) + '\nget activities*'
        (result,err) = sftp(script, folder)

def getContent():
    log = open('/tmp/logContent','w')
    print >> log, 'USB', g.USB.exists(), g.USB, (g.USB / 'content.zip').exists()
    if g.USB.exists(): #get from usb drive
         pth = g.USB / 'content.zip'
         print >> log, 'pth', pth.exists(), pth
         cmd='cp ' + pth + ' ' + target
         print >> log, cmd
         call(cmd, shell=True)
    elif isConnected:
         pth = g.SS
         script = 'cd ' + str(pth) + '\nget content.zip\n'
         (result,err) = sftp(script)
         if result:
            print >> log, 'result', result
         if err:
            print >> log, 'err', err
    else:
         call('mkdir -p content',shell=True)
         call('cp notconnected.html content/index.html',shell=True)
         log.close()
         return
    pth = target / 'content.zip'
    cmd = 'unzip -qq ' + pth
    print >> log, cmd
    call(cmd,shell=True)
    cmd = 'rm -rf ' + pth
    print >> log, cmd
    call(cmd,shell=True)
    log.close()

def getFile(filepth,filename):
    log = open('/tmp/loggetFile','w')
    pth = filepth / filename
    tgtpth = path('content') / filepth
    print >> log,'pth',pth,'tgtpth',tgtpth
    result = ''
    if g.USB.exists(): #get from usb drive
        pth = g.USB / filepth
        cmd = 'cp -r ' + pth / filename  + ' ' + tgtpth
        call(cmd,shell=True)
    else: #get from schoolserver
        pth = g.SS / filepth
        if filename.find('*') > -1:
            script = 'cd ' + str(pth) + '\nmget ' + filename
        else:
            script = 'cd ' + str(pth) + '\nget ' + filename
        (result,err) = sftp(script, tgtpth)
        if err:
            print >> log, 'getFile error', err
    return result

def _getParam(txt):
    pos1 = txt.find('var =')
    pos2 = txt.find('=')
    key = txt[pos1+5:pos2].strip()
    value = txt[pos2+1:-1].strip()
    value = value.replace("'","")
    return(key,value)

def copyFile(src,dst):
    log = open('/tmp/logcopy','w')
    cmd = 'cp ' + src + ' ' + dst
    print >> log, cmd
    try:
       call(cmd,shell=True)
    except:
       print >> log, 'cp failed', sys.exc_info()[:2]
    log.close()

activities = {
    'application/pdf':'Read',
    'application/epub+zip':'Read',
}

#execute sugar_launch
def sugarlaunch(activity, object_id, object_uri, mime_type):
    log = open('/tmp/logsl','w')
    print >> log, activity 
    print >> log, object_id
    print >> log, object_uri
    print >> log, mime_type
    if not activity:
        activity = activities[mime_type] + '.activity'
    if not activity:
        print >> log, 'no activity found matching mime_type',mime_type
        log.close()
        return
    #get bundle_id
    print >> log, activity
    bundle_id = ''
    print >> log, target.parent / activity / 'activity/activity.info'
    fin = open(target.parent / activity / 'activity/activity.info','r')
    txt = fin.read()
    fin.close()
    lines = txt.split('\n')
    for line in lines:
        if 'bundle_id' in line or 'service_name' in line:
            print >> log, 'bundle',line
            pos = line.find('=')
            bundle_id = line[pos+1:].strip()
        elif 'name' in line:
            print >> log, 'name',line
            pos = line.find('=')
            activity_name = line[pos+1:].strip() + '.activity'
    activity_name = activity
    cmd = 'sugar-launch '+ bundle_id
    print >> log, cmd
    if object_id:
        cmd = cmd +' -o '+ object_id
    elif object_uri:
        cmd = cmd +' -u '+ object_uri
    cwd = target.parent / activity_name
    print >> log, cwd, cmd
    try:
        call(cmd,cwd=cwd,shell=True)
    except:
        print >> log, 'sugar-launch failed',cmd
        print >> log, 'sugar-launch failed',cwd
        print >> log, 'sugar-launch failed',sys.exc_info()[:2]
    log.close()
