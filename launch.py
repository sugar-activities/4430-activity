#!/usr/bin/python
import sys
sys.path.append('cgi-bin')
log = open('/tmp/logLAlaunch','w')

from sugar.activity import activity
from sugar.activity.activity import get_bundle_path
from sugar.datastore import datastore
from sugar import profile

import time, os
from subprocess import call, PIPE, Popen
from path import path
import CGIHTTPServer
import BaseHTTPServer
import sha
import sqlite3
import cjson
import config as g

try:
    from activities import getContent,isConnected
except:
    print >> log, 'import failed', sys.exc_info()[:2]

_profile_path = '~/.mozilla/firefox/ukm0hbpm.default/'

firstrun = False
if not path('content').exists():
    firstrun = True
print >> log,'firstrun',firstrun

DATAPATH = path(activity.get_activity_root()) / "data"
WORKPATH = DATAPATH / "work"

class Learn(activity.Activity):
    def __init__(self, handle, create_jobject = True):
        activity.Activity.__init__(self, handle, False)
        try:
            import gconf
        except:
            g.using_gconf = False
        else:
            g.using_gconf = True
        if g.using_gconf:
            client = gconf.client_get_default()
            client.set_string('/desktop/sugar/user/role', g.role)
            print >> log, 'role',g.role
            if not g.role:
                g.role = 'staff'
        #if this is first run, must be connected to server and know role
        if firstrun:
            getContent()
        connected = isConnected()
        print >> log,'isConnected',connected
        if connected:
            call('ds-backup.sh',shell=True)
        enrollment = 'open'
        #set parameters in main.js
        if path('/content/karma').exists():
            fin = open('content/karma/js/main.js','r')
            txt = fin.read()
            fin.close()
            lines = txt.split('\n')
            txtout =  ''
            for line in lines:
                if 'var role' in line:
                    txtout += "var role = '" + role + "';\n"
                elif 'var connected' in line:
                    txtout += 'var connected = ' + connected.lower() + ';\n' 
                elif 'var enrollment' in line:
                    txtout += "var enrollment = '" + enrollment + "';\n" 
                else:
                    txtout += line + '\n'
            fout = open('content/karma/js/main.js','w')
            fout.write(txtout)
            fout.close()    
        #start Firefox
        cmd = '/usr/bin/firefox http://localhost:8008/content/index.html'
        call(cmd, shell=True)

    def close(self, skip_save = False):
        activity.Activity.close(self,True)

