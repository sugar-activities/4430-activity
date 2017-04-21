#!/usr/bin/python
import sys
import cgi, cgitb

#question types
#0 common information
#1 long answer
#2 short answer / cloze
#3 true/false
#4 multiple-choice
#30 end of quiz
quiz = []

def processQuestion(q):
    astart = q.find('{')
    aend = q.find('}')
    if astart < 0:
        a = ''
        t = 0
    else:
        t = 2
        a = q[astart:aend+1]
        if len(q)>aend+1:
            q = q[:astart] + '____'+q[aend+1:]
        else:
            q = q[:astart]
        if a == '{}':
            t = 1
        elif not '=' in a:
            t = 3
        elif '~' in a:
            t = 4
    return str(t)+'|'+q+'|'+a

cgitb.enable(display=True)
log = open('/tmp/logGetQuiz','w')
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
f = form.getfirst('filename')
#set up list of questions,answers
fin = open(f, 'r')
txt = fin.read()
fin.close()
lines = txt.split('\n')
print >> log, len(lines)
for line in lines:
    print >> log,line
print >> log,'_____________________________________'
flag = False
quizflag = False
q = ''
a = ''
count = 0
for line in lines:
    count += 1
    n = str(count)
    if not quizflag:
        if '<!--Quiz' in line:
            quizflag = True
    elif '-->' in line:
        quizflag = False
    else:
        if flag and not line:
            print >> log,'processQuestion',q
            tstr = processQuestion(q)
            quiz.append(tstr)
            t = 2
            q = ''
            a = ''
            flag = False
        elif flag:
            q = q +line
        elif line:
            q = q + line
            flag = True
if flag:
    tstr = processQuestion(q)
    quiz.append(tstr)
quiz.append('30||')
txtout=''
tcount = 0
for item in quiz:
    if item:
        tcount+=1
        txtout += item + '\n'
print txtout
print >> log
print >> log,'txtout=',len(quiz),tcount
print >> log, txtout
print >> log
log.close()
