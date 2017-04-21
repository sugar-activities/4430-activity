#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path
from sugar.datastore import datastore
from gifted import gifted

src = path('~/Documents/')

html = "<li id=xxxx onclick=manageQuiz('xxxx','yyyy')>"
html = html+"<p>xxxx</p></li>"
mime_types = ['text/plain']

#script to construct jquery quiz from gift file into activity - quiz.js
#and update source.txt with markup
#list files in Journal and ~/Documents matching quiz*.txt -python returns list
#user selects quiz - javascript
#copy quiz file to temp - python
#convert file to quiz.js in activity folder - python gifted.py 
#create markup in source.txt - python
#refresh Content Edit screen - javascript
log = open('/tmp/logQuiz','w')
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
print >> log, form
quiz = form.getfirst('quiz',default='')
pth = form.getfirst('pth')
print >> log, 'quiz',quiz,'pth',pth
if quiz:
    #read file and pass string to gifted
    print >>log, 'quiz=',quiz
    try:
        fin = open(src / quiz+'.txt','r')
        txt = fin.read()
        fin.close()
    except:
        print >> log, 'read quiz failed',sys.exc_info()[:2]
    else:
        print >> log, 'read quiz succeeded',len(txt),txt
    try:
        quiz = gifted(txt)
    except:
        print >> log, 'gifted failed',sys.exc_info()[:2]
    else:
        print >> log,'quiz',len(quiz),quiz
    #insert quiz in source.txt
    try:
        fin = open(path(pth) / 'source.txt','r')
        txt = fin.read()
        fin.close()
    except:
        print >> log, 'read source.txt failed',sys.exc_info()[:2]
    txtout = quiz + txt
    print >> log, 'write source.txt',pth,txtout
    try:
        fout = open(path(pth) / 'source.txt','w')
        fout.write(txtout)
        fout.close()
    except:
        print >> log,'rewrite source.txt failed',sys.exc_info()[:2]
    else:
        print >> log,'rewrite source.txt succeeded'
else: #return list of quizzes in gift format ('quiz*.txt') - one per line
    print >> log, 'return list of available quizzes'
    #for each item in the datastore
    ds_objects, num_objects = datastore.find({},properties=['uid','title','mime_type'])
    print >> log,'num_objects',num_objects
    for i in xrange(0,num_objects,1):
        title = ds_objects[i].metadata['title']
        mime = ds_objects[i].metadata['mime_type']
        #if item is text/plain
        if mime in mime_types:
            #copy clip to ~/Documents
            clip = ds_objects[i].get_file_path()
            if 'quiz' in title and 'txt' in title:
                cmd = 'cp ' + clip + ' ' + '~/Documents/'+title
                print >> log, cmd
                subprocess.call(cmd,shell=True)
    #list files 'quiz*.txt' in ~/Documents
    quizlist = path('~/Documents').files('quiz*.txt')
    print >> log,len(quizlist),quizlist
    for quiz in quizlist:
        #print line for <ul>
        title = path(quiz).namebase
        line1 = html.replace('yyyy',str(pth))
        line = line1.replace('xxxx',title)
        print >> log, line
        print line
log.close()
