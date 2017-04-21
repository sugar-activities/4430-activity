#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from buildLesson import buildLesson
from buildMenu import buildMenu
from path import path

def cleanQuiz(txt,pos1,pos2):
    comment = txt[pos1:pos2]
    comment = comment.replace('/*','<!--')
    comment = comment.replace('*/','-->')
    if '/*Quiz' in comment and not '<pre>' in txt[pos1-6:pos2]:
        lines = comment.split('\n')
        txtout = ''
        for line in lines:
            line = line.replace('<p>','')
            line = line.replace('</p>','')
            line = line.replace('&nbsp;','')
            txtout += line + '\n'
        comment = '\n<pre>\n'+txtout+'\n</pre>\n'
    return comment

cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
log = open('/tmp/logs','w')
form = cgi.FieldStorage()
print >> log, 'form',form
f = form.getfirst('fn')
txt = form.getfirst('txt')
fpth = path(f).parent
savepth = fpth / 'source.txt'
menupth = fpth / 'index.html'
print >>log,'fpth',fpth
print >>log,'txt',len(txt)
#convert visible comments to real html comments
done = False
while not done:
    pos=txt.find('/*')
    if pos<0:
        done = True
        continue
    pos1=txt.find('*/')
    comment = cleanQuiz(txt,pos,pos1+2)
    txt = txt[:pos]+comment+txt[pos1+2:]
if txt:
    txt = txt.replace('\t','')
    lines = txt.split('\n')
    txtout = ''
    for line in lines:
	txtout += line + '\n'
    u = '\xa0'
    txtout = txtout.replace(u,'')
    txtout = txtout.replace('&nbsp;',' ')
    try:
        fout = open(savepth,'w')
        fout.write(txtout)
        fout.close()
    except:
        print >> log, 'save failed',sys.exc_info()[:2]
try:
    addl,adds=buildLesson(fpth)
except:
    print >> log, 'buildLesson failed',sys.exc_info()[:2]
else:
    print >> log, 'buildLesson succeeded'
    print >> log,'added',addl,adds
try:
    result = buildMenu('activity',added_links=addl,added_scripts=adds)
    fout = open(menupth,'w')
    fout.write(result)
    fout.close()
except:
    print >> log, 'buildMenu failed',sys.exc_info()[:2]
else:
    print >> log, 'buildMenu succeeded'
log.close()

