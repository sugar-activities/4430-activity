#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path
cgitb.enable(display=True)
AUDIOPATH = '/tmp/audio.wav'

# Start Recording
def record(filename):
    if not filename :
        #we are recording, stop and save clip
        subprocess.call("killall -q arecord", shell=True)
        #convert to ogg file
        #initialize convert pipeline
        pipeline = "filesrc location=" + AUDIOPATH + " ! wavparse "
        pipeline += "! audioconvert ! vorbisenc ! oggmux "
        pipeline += "! filesink location="
        pipeline += filename
        subprocess.call("gst-launch-0.10 " + pipeline, shell=True)
        #reset mic boost
        subprocess.call("amixer cset numid=11 off", shell = True)()
    else:
        #turn on mic boost (xo)
        subprocess.call("amixer cset numid=11 on", shell=True)
        pid=subprocess.Popen("arecord -f cd " + AUDIOPATH, shell=True)

print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
f = form.getfirst('filename')
record(f)
