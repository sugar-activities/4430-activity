#!/usr/bin/python
import sys, subprocess
import cgi, cgitb
from path import path
from BeautifulSoup import BeautifulSoup
sys.stderr = sys.stdout
basepath = path('/home/tony/Desktop/siyavula_edit')
th = "<!DOCTYPE html><html><head></head><body>"
tf = "</body></html>"
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
f = form.getfirst('filename', default='none')
txt = form.getfirst('content', default='<h1>notext</h1>')
soup = BeautifulSoup(txt)
imgs = soup.findAll('img')
for img in imgs:
    img['src']= path(img['src']).name
txt = soup.prettify()
count = 0
done = False
print >> sys.stderr, 'done', done, f, len(txt)
if len(str(f)) > 0:
    fo = ""
    txtout = ""
    while not done:
        count += 1
        pos = txt.find('<hr')
        if pos < 0:
            tout = txt
            print >> sys.stderr, 'done'
            done = True
        else:
            tout = txt[:pos]
            txt = txt[pos+6:]
        k = str(count)
        if len(k)< 2:
            k = '0'+k
        txtout = BeautifulSoup(th + tout + tf).prettify()
        fo = basepath / 'b'+k+'.html'
        print >> sys.stderr, fo
        fout = open(fo,'w')
        fout.write(txtout)
        fout.close()




