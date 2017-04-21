#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path
from activities import sftp
from activities import 	sugarlaunch
from sugar.datastore import datastore
from sugar.activity import activity

target = path('~/.sugar/default/rw.olpc.Learn/instance')

def process1():
    cgitb.enable(display=True)
    print 'Content-Type:text/html\n\n'
    try:
        form = cgi.FieldStorage()
    except:
        print >> log,'form retrieval failed', sys.exc_info()[:2]
    f = path(form.getfirst('filename'))
    t = form.getfirst('title')
    m = form.getfirst('mime_type')
    l = form.getfirst('language')
    return f, t, m, l

def process2(f, t, m, l, log):
    #get from library
    print >> log, 'in process2:params=',f,t,m,l 
    library = path('/library/media')
    scrpt = 'cd ' + library / l / str(f.parent).lower()  + '\nget '+ f.name + '\n'
    print >> log, 'script',scrpt,'target', target
    result, error = sftp(scrpt,folder=target)
    print >> log, 'sftp result',len(result),result,'error',len(error),error

log = open('/tmp/logDownload','w')
print >> log, 'log open'
try:
    f,t,m,l = process1()
except:
    print >> log, 'process1 failed', sys.exc_info()[:2]

print >> log, 'entering process 2'
try:
    process2(f,t,m,l,log)
except:
    print >> log, 'process2 failed', sys.exc_info()[:2]

#add to journal
print >> log, 'add to journal', f, t, m, l
if m == 'application/vnd-olpc-sugar':
    #download and install
    try:
        cmd = 'sugar-install-bundle ' + path(target) / f.name
    except:
        print >> log, 'problem', sys.exc_info()[:2]
    print >> log, 'install bundle', cmd
    try:
        pid = subprocess.Popen(cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True)
    except:
        print >> log, 'Popen failed',sys.exc_info()[:2]
    (result,err) = pid.communicate()
    if result:
        print >> log, 'result',result
    if err:
        print >> log, 'error', err
    print >> log, 'activity installed'
    #now we need to find out the unzipped folder name
    #then we need to delete the xo bundle and unzipped folder
    cmd = 'unzip ' + target / f.name
    cwd = target
    print >> log, cmd, cwd
    subprocess.call('unzip ' + target / f.name, cwd = cwd, shell=True)
    folders = target.dirs()
    for folder in folders:
        if 'activity' in str(folder):
            activity = folder.name
        subprocess.call('rm -rf ' + folder,shell=True)
    print >> log, 'activity folder for sugarlaunch', activity
    try:
        sugarlaunch(activity, '', '','application/vnd-olpc-sugar')
    except:
        print >> log, 'sugarlaunch failed', sys.exc_info()[:2]
    print >> log, 'sugarlaunch',activity,'launched'   
else:
    #download to Journal
    activity = ''
    dsobject = datastore.create()
    dsobject.metadata['title']=t
    dsobject.metadata['mime_type']=m
    dsobject.set_file_path(target / f.name)
    print >> log, 'file_path=', target / f.name
    datastore.write(dsobject)
    #DSObject.destroy()
    subprocess.call('rm -rf ' + target / f.name, shell=True)
    print >> log, 'item added to Journal'
    print >> log, 'sugarlaunch',activity, m
    try:
        sugarlaunch(activity,dsobject.object_id,'',m)
    except:
        print >> log, 'sugarlaunch failed', sys.exc_info()[:2]
log.close()
