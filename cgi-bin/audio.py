#!/usr/bin/python
import os, sys
from subprocess import call, Popen, PIPE
import cgi, cgitb
from path import path
from sugar.datastore import datastore

html = "<li id=xxxx onclick=manageAudio('xxxx','yyyy')>"
html = html+"<p>xxxx</p></li>"
ogg_types = ['audio/ogg']

#script to insert audio clip in activity - source.txt
#list clips in Journal -python returns list
#user selects clip - javascript
#show mock up of screens - javascript
#user selects screen - javascript
#copy clip to activity folder - python
#create markup in source.txt - python
#refresh Content Edit screen - javascript
#python knows because of form:

cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
clip = form.getfirst('clip')
pth = form.getfirst('pth')
log = open('/tmp/logAudio','w')
print >> log, 'clip', clip, 'pth', pth
if clip: #copy clip to activity
    clip = clip.replace(' ','_')
    src = '/home/olpc/Documents/' + clip
    cmd = 'cp ' + src + ' ' + pth +'/'  + clip
    print >> log, cmd
    pid = Popen(cmd,stdout=PIPE,stderr=PIPE,shell=True)
    result, err = pid.communicate()
    if result:
        print >> log, 'cp result',result
    if err:
        print >> log, 'cp err',err
    try:
        fin = open(path(pth) / 'source.txt','r')
        txt = fin.read()
        fin.close()
    except:
        print >> log, 'read source.txt failed',sys.exc_info()[:2]
    txtout = '<!--A1_'+clip+'-->\n'+txt
    print >> log, 'write source.txt',pth
    try:
        fout = open(path(pth) / 'source.txt','w')
        fout.write(txtout)
        fout.close()
    except:
        print >> log,'write source.txt failed',sys.exc_info()[:2]
else: #return list of clips - one per line
    #for each item in the datastore
    ds_objects, num_objects = datastore.find({},properties=['uid','title','mime_type'])
    for i in xrange(0,num_objects,1):
        title = ds_objects[i].metadata['title']
        mime = ds_objects[i].metadata['mime_type']
        #if item is an audio clip
        if mime in ogg_types:
            #copy clip to /home/olpc/Documents
            clip = ds_objects[i].get_file_path()
            title = path(title).namebase+'.ogg'
            title = title.replace(' ','_')
            cmd = 'cp ' + clip + ' ' + '/home/olpc/Documents/'+title
            print >> log, cmd
            pid=Popen(cmd,stdout=PIPE,stderr=PIPE,shell=True)
            result,err = pid.communicate()
            if result:
                print >> log,'cp clip to Documents result',result
            if err:
                print >> log,'cp clip to Documents err',err
            #print line for <ul>
            line1 = html.replace('yyyy',str(pth))
            line = line1.replace('xxxx',title)
            print >> log, line
            print line
print >> log, 'done'
log.close()
