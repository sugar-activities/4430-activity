#!/usr/bin/python

import os, sys, subprocess
from sugar.activity import activity
import cgi, cgitb
from path import path
import activities
from activities import getNick
from activities import getInstalled
from activities import getActivitiesJs
from activities import fetchMilestone
from activities import getMilestones
from activities import getActivities
from activities import setMilestones
from activities import setActivities

DATAPATH = path(activity.get_activity_root())/ 'data'
WORKPATH = DATAPATH / 'work'
USB = path('/media/2011/courseware')
SS = path('/library/courseware')

log = open('/tmp/logfm','w')

def process_milestones(subject, grade, current_ms):
    #base on activities.js not milestone name
    #need to get milestones as list where current_ms is index
    fin = open('content/'+subject+'/activities_'+grade.lower()+'.js','r')
    txt = fin.read()
    fin.close()
    lines = txt.split('\n')
    milestones = []
    for line in lines:
        try:
            milestone = eval(line)[0]
        except:
            continue
        milestones.append(milestone)
    current_milestone = milestones[int(current_ms)-1][4]
    next_milestone = milestones[int(current_ms)][4]
    installed = getInstalled(subject)
    if len(installed) < 1:
        initialFlag = True
    else:
        initialFlag = False
    if not current_milestone in installed:
        fetchMilestone(subject, grade, current_milestone)
        milestones = getMilestones(subject, grade)
        for milestone in milestones:
            if milestone[4] == current_milestone:
                milestone[5] = 'blue'
        setMilestones(subject,grade,milestones)
    if not next_milestone in installed:
        fetchMilestone(subject, grade, next_milestone)
        milestones = getMilestones(subject, grade)
        for milestone in milestones:
            if milestone[4] == next_milestone:
                milestone[5] = 'blue'
        setMilestones(subject,grade,milestones)
    if initialFlag and not mode == 'faculty':
        #mark first milestone and first activity red
        milestones = getMilestones(subject, grade)
        entry = milestones[0]
        entry[5] = 'red'
        milestone = entry[4]
        setMilestones(subject, grade, milestones)
        activities = getActivities(subject, milestone)
        activities[0][5] = 'red'
        setActivities(subject, milestone, activities)

def process_student(student,student_record):
    grade = student_record['grade']
    en_milestone = student_record['milestones'][0]
    ma_milestone = student_record['milestones'][1]
    #copy activities.js for grade to activities.js
    src = path('content') / 'English/activities_'+ grade.lower() + '.js'
    dst = path('content') / 'English' / 'activities.js'
    if not dst.exists():
        cmd = 'cp ' + src + ' ' + dst
        subprocess.call(cmd,shell=True)
    src = path('content') / 'Mathematics/activities_'+ grade.lower() + '.js'
    dst = path('content') / 'Mathematics' / 'activities.js'
    if not dst.exists():
        cmd = 'cp ' + src + ' ' + dst
        subprocess.call(cmd,shell=True)
    #return student menu
    fin = open('menu/student_menu','r')
    txt = fin.read()
    fin.close()
    print txt
    #download needed milestones
    #English
    current_ms = en_milestone.split('.')[0]
    process_milestones('English',grade, current_ms)
    #Mathematics
    current_ms = ma_milestone.split('.')[1]
    process_milestones('Mathematics',grade, current_ms)

def setColor(subject, grade, milestone, color):
    milestones = getMilestones(subject, grade)
    for ms in milestones:
        if ms[4] == milestone:
            ms[5] = color
            setMilestones(subject, grade, milestones)
    milestones = getMilestones(subject, grade) 
    for ms in milestones:
        if ms[4] == milestone:
            ms[5] = color
            setMilestones(subject, grade, milestones)

def process_faculty():
    sbj = form.getfirst('code', default="")
    if len(sbj) < 1:
        #if firstrun, need only to return faculty main menu for #content
        fin = open('menu/faculty_menu','r')
        txt = fin.read()
        fin.close()
        print txt
    else:
        if sbj[:2] == 'en':
            subject = 'English'
        else:
            subject = 'Mathematics'
        grade = sbj[2:]
        milestone = form.getfirst('milestone', default = "")
        try:
            fetchMilestone(subject,grade,milestone)
        except:
            print >> log, 'fetchMilestone failed',sys.exc_info()[:2]
        try:
            setColor(subject, grade, milestone, 'blue')
        except:
            print >> log, 'setColor failed', sys.exc_info()[:2]

#main
#
#get paramters: mode, year, milestone, student name
#
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
#if milestone activities.js not installed, install them
pth = path('content') / 'English'
fs = pth.files('*.js')
if len(fs) < 3:
    #get them
    getActivitiesJs('English')
pth = path('content') / 'Mathematics'
fs = pth.files('*.js')
if len(fs) < 3:
    #get them
    getActivitiesJs('Mathematics')
#get nick
nickname = getNick()
#read student record
fin = open(DATAPATH / nickname, 'r')
txt = fin.read()
fin.close()
student_record = eval(txt)
grade = student_record['grade']
if grade[0] == 'F':
    mode = 'faculty'
else:
    mode = 'student'
print >> log, mode
if mode == 'faculty':
    try:
        process_faculty()
    except:
        print >> log, 'process_faculty failed',sys.exc_info()[:2]
else:
    try:
        process_student(learner,student_record)
    except:
        print >> log, 'process student failed', sys.exc_info()[:2]
print >> log, 'done'
log.close()

