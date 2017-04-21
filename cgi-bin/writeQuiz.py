#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path


log = open('/tmp/logWQ','w')
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
txt = form.getfirst('text', default='var quiz = {\n        []\n}\n')
print >> log, 'txt', txt
activity = form.getfirst('activity', default='savefile')
print >> log, 'activity', activity
opt = 'var options = {\n'
opt = opt + '    random:false,\n'
opt = opt + '    allRandom:false,\n'
opt = opt + '    disableRestart:true,\n'
opt = opt + '    disableDelete:true,\n'
opt = opt + '    title: "Opportunity",}\n'
txt = 'var quiz = {\nfill:[\n' + txt + ']\n};\n\n' + opt + '\n'
print >> log, 'quiz', txt
# write quiz
pth = path(activity) / 'quiz.js'
print >> log, 'path', pth
fout = open(pth,'w')
fout.write(txt)
fout.close()
log.close()
