#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path
#import gstream
import pygst
pygst.require("0.10")
import gst

logpth = path('/tmp') / 'logplay'
if logpth.exists():
    logpth = path('/tmp') / 'logplay1'
cgitb.enable(display=True)
log = open(logpth,'w')
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
print >> log, 'form',form
src = path(form.getfirst('src'))
print >> log, 'src', src
if src.exists():
    print >> log, 'src path exists?'
else:
    src = 'content/karma/audio/' + src.name
    print >> log, 'updated src', src
# Play Audio Clip
def play(src):
    #play clip
    cmd = "gst-launch-0.10 filesrc location=" + src
    cmd = cmd  + " ! decodebin ! audioconvert ! alsasink"
    pid = subprocess.Popen(cmd, shell=True)
    print >>log,'play:',cmd
# Stop Audio Clip
def stop():
    #we are playing and need to stop
    subprocess.call('killall -q gst-launch-0.10',shell=True)
    print >>log,'stop'

if src:
    play(src)
else:
    stop()

log.close()
