#!/usr/bin/env python

import sys
import cgi, cgitb
from path import path
#
#getIndex is called from ready()
#it returns a dictionary with key entries for each subject
#the value is a list containing a list for each class
#the class list contains the number of activities for each milestone
#exceptions: milestone 3_1 and 3_2 need to be renumbered
# 
print 'Content-Type:text/html\n\n'
subjects = ['English', 'Mathematics']
contents = []
d = path('/media/2011/courseware')
for subject in subjects:
    pth = d / subject
    course = []
    units = pth.dirs()
    units.sort()
    grade = []
    cgrade = 1
    for unit in units:
        if int(unit.name[3]) > cgrade:
            course.append(grade)
            grade = []
            cgrade = int(unit.name[3])
        activities = unit.files('a*.txt')
        grade.append(len(activities))
    contents.append(course)
print str(contents)
