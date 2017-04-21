#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from sugar.activity import activity
from path import path
cgitb.enable(display=True)
log = open('/tmp/logFF','w')
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
page = form.getfirst('page', default='none given')
print >> log, 'page', page
cmd = '/usr/bin/firefox file://'+activity.get_bundle_path()+'/'+page+'&'
print >> log,cmd
subprocess.call(cmd,shell=True)
log.close()
