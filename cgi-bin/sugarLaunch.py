#!/usr/bin/python

import sys
import cgi, cgitb
import subprocess
from path import path
from sugar.activity import activity
from sugar.datastore import datastore

target = path(activity.get_bundle_path())
sys.stderr = sys.stdout
cgitb.enable(display=True)

print 'Content-Type:text/html\n\n'
#execute sugar_launch
log = open('/tmp/logsl','w')
form = cgi.FieldStorage()
activity = form.getfirst('activity', default='') + '.activity'
object_id = path(form.getfirst('bundle', default=''))
object_uri = form.getfirst('uri', default = '')
mime_type = form.getfirst('mime', default = '')
print >> log,'form',activity,'id',object_id,'uri',object_uri,mime_type
#get bundle_id
bundle_id = ''
try:
    pth = target.parent / activity / 'activity/activity.info'
except:
    print >> log, 'pth failed',sys.exc_info()[:2]
else:
    print >> log, 'open path',pth
try:
    fin = open(pth,'r')
    txt = fin.read()
    fin.close()
except:
    print >> log,'open file failed',sys.exc_info()[:2]
    txt=''
lines = txt.split('\n')
print >> log,'lines',len(lines)
for line in lines:
    if 'bundle_id' in line or 'service_name' in line:
        pos = line.find('=')
        bundle_id = line[pos+1:].strip()
print >> log,'bundle_id',bundle_id
if object_id:
    #insert bundle in Journal
    dsobject = datastore.create()
    dsobject.metadata['activity']=bundle_id
    dsobject.metadata['title']=object_id.namebase
    dsobject.metadata['mime_type']=mime_type
    dsobject.set_file_path(target / object_id)
    datastore.write(dsobject)
cmd = 'sugar-launch '+ bundle_id
print >> log,'cmd',cmd
if object_id:
    cmd = cmd +' -o '+ dsobject.object_id
elif object_uri:
    cmd = cmd +' -u '+ object_uri
cwd = target.parent / activity
print >> log, cwd, cmd
subprocess.call(cmd,cwd=cwd,shell=True)
log.close()
