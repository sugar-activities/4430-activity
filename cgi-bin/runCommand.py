#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb

base = 'file://'+activity.get_bundle_path()
cgitb.enable(display=True)
log = open('/tmp/logPF','w')
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
pth = form.getfirst('pth')
#now play pth 
cmd = 'firefox file://' + base + pth
print >>log, 'cmd', cmd
subprocess.call(cmd,shell=True)
log.close()
