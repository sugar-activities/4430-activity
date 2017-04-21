#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from sugar.activity import activity
from activity import isConnected, getRole
cgitb.enable(display=True)
log = open('/tmp/logParms','w')
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
print isConnected(), getRole()
log.close()
