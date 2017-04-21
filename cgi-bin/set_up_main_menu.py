#!/usr/bin/python

#set up activities.js for English/English11,Mathematics/Mathematics11
#gets list of installed milestones for subject, year
#creates activities.js
#assumes milestones are already set up correctly

from sugar.activity import activity
from sugar.datastore import datastore
import subprocess, time, sys
from path import path
import CGIHTTPServer
import BaseHTTPServer
import cgi, cgitb

DATAPATH = path(activity.get_activity_root())/ 'data'
SUBJECTS = ['English', 'Mathematics']
MILESTONES = {'English':[5,8,8],'Mathematics':[15,18,18]}

def get_student_record(student):
    #read student record
    fin = open(DATAPATH / student,'r')
    txt = fin.read()
    fin.close()
    student_record = eval(txt)
    return student_record

def get_installed(subject):
    pth = path('content') / subject
    folders = pth.dirs()
    milestones = []
    for milestone in folders:
        milestones.append(milestone.namebase)
    milestones.sort()
    milestones.remove('karma')
    return milestones

def create_student_activities_list(current_milestone, current_activity):
    #create full list for specified class
    #current milestone color is red, preceding are chartreuse or green, following are 
    #blue or cyan, use installed milestones to set colors
    # entry = ['0','0','milestone','m','x','color']

    #first update subject activities.js
    print >> log,'csal',current_milestone,current_activity
    grade = current_milestone[2:4]
    subject = current_milestone[:2]
    if subject == 'en':
        sbj = 'English'
    else:
        sbj = 'Mathematics'
    print >> log, 'csal', grade, subject, sbj
    milestones = MILESTONES[sbj]
    print >> log, 'csal milestones', milestones
    installed = get_installed(sbj)
    print >> log, 'csal installed', installed
    all = milestones[int(grade[1])-4]
    print >> log, 'csal all',all
    #we add a line for each milestone
    txtout = 'var activities = [\n'
    print >> log, 'create_student_activities_list', all
    for ms in range(all):
        #construct milestone_name in form 'enp4m01' or 'map5m01' - assume only term 1
        strms = str(ms+1)
        if len(strms)<2:
            strms = '0' + strms
        milestone_name = subject + grade.lower() + 'm' + strms
        print >> log, 'csal milestone_name',milestone_name
        newentry = []
        newentry.append('0')
        newentry.append(strms)
        newentry.append('milestone')
        newentry.append(milestone_name[:4])
        newentry.append(milestone_name)
        if ms+1<int(current_ms):
           if milestone_name in installed:
                color = 'green'
           else:
                color = 'chartreuse'
        elif ms+1>int(current_ms):
           if milestone_name in installed:
                color = 'blue'
           else:
                color = 'cyan'
        else:
                color = 'red'
        newentry.append(color)
        txtout = txtout + str(newentry) + ',\n'
    txtout = txtout + '];\nvar assetList = [];\nvar logos = [];\n'
    #write activities.js		
    pth = path('content') / sbj
    print >> log, 'write activities.js', pth, txtout
    fout = open(pth / 'activities.js','w')
    fout.write(txtout)
    fout.close()
    print >>log, 'subject activities.js written', pth
    #now we need to update the activities.js for the milestone activities.js
    #assume existing activities.js is correct except for colors
    tpth = pth / current_milestone / 'activities.js'
    print >> log, 'update milestone activities.js', tpth
    fin = open(tpth,'r')
    txt = fin.read()
    fin.close()
    txtout = ''
    lines = txt.split('\n')
    print >>log, 'csal number lines', len(lines)
    for line in lines:
        #normalize colors to lower case
        t1 = line.replace('Blue','blue') + '\n'
        t2 = t1.replace('Red','red')
        t3 = t2.replace('red','blue')
        if current_activity in line:
             print >> log, 'csal', current_activity, t3
             txtout = txtout + t3.replace('blue','red')
        else:
             txtout = txtout + t3
    fout = open(tpth,'w')
    fout.write(txtout)
    fout.close()

def create_activities_list(subject, milestones):
#let's create a new activities.js file based on installed milestones
    print >> log,'in create_activitie_list!!!'
    entry = ['0','0','milestone','m','x','color']
    #we add a line for each milestone that is installed
    txtout = 'var activities = [\n'
    print >> log, 'create_activities_list', milestones
    for milestone in milestones:
        ms = str(path(milestone).namebase)
        if ms[len(ms)-2] == 'm':
            t = ms[-1:]
        else:
            t = ms[-2:]
        newentry = entry
        newentry[1] = ms[3]+'.'+ t
        newentry[3] = ms[:4]
        newentry[4] = ms
        newentry[5] = 'Blue'
        txtout = txtout + str(newentry) + ',\n'
    txtout = txtout + '];\nvar assetList = [];\nvar logos = [];\n'
    #write activities.js
    pth = path('content') / subject
    print 'write activities.js', pth, txtout
    fout = open(pth / 'activities.js','w')
    fout.write(txtout)
    fout.close()
    print >>log, 'activities.js written', pth

def update_control_menu(subject, grade, term, milestones):
    #read p*.js for subject and grade
    #for each entry - set color to Cyan
    #if path to milestone exists, set color to Blue
    if term == 0:
        pth = 'content/'+subject+'/p'+str(grade)+'.js'
    else:
        pth = 'content/'+subject+'/p'+str(grade)+str(term)+'.js'
    fin = open(pth,'r')
    txt = fin.read()
    fin.close()
    lines = txt.split('\n')
    txtout = ''
    for line in lines:
        result = line.find('Blue') < 0 and line.find('Cyan') < 0
        if result:
            txtout = txtout + line + '\n'
            continue
        entry=eval(line)[0]
        milestone = entry[4]
        if milestone in milestones:
            entry[5] = 'Blue'
        else:
            entry[5] = 'Cyan'
        txtout = txtout + str(entry) + ',\n'
    print pth, txtout
    fout = open(pth,'w')
    fout.write(txtout)
    fout.close()

def trim_milestones(subject, grade):
    #in subject, remove all milestones other than grade
    #if more than four milestones in grade, remove excess starting at lowest
    pth = path('content/') /  subject
    print >> log, 'trim_milestones', subject, grade, pth
    try:
        milestones = get_installed(subject)
    except:
        print >> log,'get_installed failed',sys.exc_info()[:2]
    print >> log, 'trim_milestones',pth,len(milestones),milestones
    for milestone in milestones:
        if not milestone[2:4] == grade.lower():
            subprocess('rm -rf ' + pth + '/' + milestone,shell=True)
    milestones = get_installed(subject)
    milestones.sort()
    n = len(milestones)-4
    if n>0:
        for i in range(n):
            subprocess('rm -rf ' + pth + '/' + milestones[i],shell=True)
     

#start main processing
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
log = open('/tmp/log','w')
form = cgi.FieldStorage()
mode = form.getfirst('mode',default = 'CW')
print >> log, 'mode', mode
if not mode=='CW':
    student = form.getfirst('student', default='unknown')
    subject = form.getfirst('subject', default='unknown')
    print >> log, 'form', mode, student, subject
    #read student record for grade, current_milestones
    student_record = get_student_record(student)
    grade = student_record['grade']
    print >> log, student, grade
    #remove excess milestones in subject (other grades, more than four from m01)
    try:
        trim_milestones(subject, grade)
    except:
        print >> log, 'trim_milestones failed', sys.exc_info()[:2]
    #update activities.js for subject
    milestones = student_record['milestones']
    if subject == 'English':
        sbj = 'en'
    else:
        sbj = 'ma'    
    t = milestones[0].split('.')
    current_ms = t[0]
    if len(current_ms)<2:
        current_ms= '0'+current_ms
    current_act = t[1]
    if len(current_act)<2:
        current_act='0'+current_act
    print >> log, 'current',  t, current_ms, current_act
    current_milestone = sbj+grade.lower()+'m'+current_ms
    current_activity = current_milestone+'a'+current_act
    print >> log, 'create_student_activities_list',current_milestone,current_activity
    try:
        create_student_activities_list(current_milestone,current_activity)
    except:
        print >> log, 'create_student_activities_list failed', sys.exc_info()[:2]
    print >> log,'created student activities list',current_milestone, current_activity
else:
    for subject in SUBJECTS:
        if mode == 'CW':
            terms = 3
            grades = 3
            delta = 4
            subject = subject+'11'
        else:
            terms = 1
            grades = 6
            delta = 1
        print >> log, 'mode', mode, 'subject', subject, 'grades', grades, 'terms',terms
        milestones = get_installed(subject)
        print >> log, 'create_activities_list', subject, milestones
        create_activities_list(subject, milestones)
        print >> log, 'created activities_list', subject
        for grade in range(grades):
            for term in range(terms):
                update_control_menu(subject, grade+delta, term+1, milestones)
print >> log, 'done'
log.close()
        
