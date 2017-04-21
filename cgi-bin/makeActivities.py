#!/usr/bin/python
import os, sys, subprocess
from sugar.activity import activity
import cgi, cgitb
from path import path
from activities import setEntries
from buildMenu import buildMenu
from buildLesson import buildLesson

log=open('/tmp/logM','w')

cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
subject = form.getfirst('subject')
course = form.getfirst('course')
milestone = form.getfirst('milestone',default='')
rows = form.getfirst('rows')
print >> log, len(rows),rows
temp1 = rows.replace(',\n',',')
temp  = temp1.split('\n')
print >> log, subject, course, milestone
if milestone:
    base = path('content') / subject / course / milestone
else:
    base = path('content') / subject / course
entries = []
for item in temp:
    entry = item.split(',')
    print >> log, 'entry', entry
    entries.append(entry)
if not milestone:
    #and create an empty milestone folder
    templist = []
    for entry in entries:
        #assign entry[4] the next available 
        #folder name in form msxx where xx is a two-digit number
        #from entries make list of folder names
        if entry[4]:
            templist.append(entry[4])
    print >> log,'templist',templist
    for entry in entries:
        print >> log,'entry',entry
        if entry[4]:
            continue #we only need folders for new milestones
        print >> log,'new entry',entry
        count = 0     
        done = False
        while not done:
            count += 1
            n = str(count)
            if len(n)<2:
                n = '0'+n
            folder='ms'+n
            if not folder in templist:
                templist.append(folder)
                entry[4]=folder
                pth = base / folder
                print >> log,'pth',pth
                done = True
        print >> log,'write files for',entry
        try:
            subprocess.call('mkdir '+pth,shell=True)
            txtout = 'var activities = [\n];\n'
            fout = open(pth / 'activities.js','w')
            fout.write(txtout)
            fout.close()
            result = buildMenu('lesson')
            fout = open(pth / 'index.html','w')
            fout.write(result)
            fout.close()
        except:
            print >> log, 'write files failed',sys.exc_info()[:2]
        else:
            print >> log, 'write files successful'
else:
#create an empty activity
    for entry in entries:
        if entry[4]:
            continue #only handle new activities
        print >> log,'add activity',entry
        #assign entry[4] the next available
        #folder name in form axx where xx is a two-digit number
        done = False
        count = 0
        while not done:
            count += 1
            n = str(count)
            if len(n)<2:
                n = '0'+n
            entry[4]='a'+n
            pth = base / entry[4]
            print >> log,'pth',pth
            if not pth.exists():
                done = True
        print >> log,'prepare new activity',pth
        subprocess.call('mkdir '+pth,shell=True)
        #here handle templates
        #entry[3] = 't00..t20'
        template_type = entry[3].strip()
        print >> log, 'template_type',template_type
        entry[3] = 'basic'
        if not template_type[0] == 't':
            template_type = 't00'
        if  template_type =='t00':
            fout = open(pth /'source.txt','w')
            fout.write('<h1>This is a new activity.<h1>')
            fout.close()
        else:
            #copy contents of template to new activity
            try:
                src = path(activity.get_bundle_path()+'/content/karma/templates/')
            except:
                print >> log,'get bundle path failed',sys.exc_info()[:2]
            cmd = 'cp -r ' + src / template_type / '* ' + pth
            print >> log,'copy activity',cmd
            subprocess.call(cmd,shell=True)
        try:
            addl,adds=buildLesson(pth)
        except:
            print >> log, 'buildLesson failed',sys.exc_info()[:2]
        else:
            print >> log, 'add',addl,adds
            try:
                result = buildMenu('activity',added_links=addl,added_scripts=adds)
            except:
                print >> log, 'buildMenu failed',sys.exc_info()[:2]
            else:
                print >> log, 'pth',pth,'buildMenu',result
                fout = open(pth / 'index.html','w')
                fout.write(result)
                fout.close()
#here we need to setEntries for a course or milestone
setEntries(subject, course, milestone, entries)
log.close()
