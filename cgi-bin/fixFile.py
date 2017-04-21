n#!/usr/bin/python
"""
This version acts as cgi script, applying selected conversions
to a file supplied in the form

get form parameters
make soup
apply conversions
make txt
return
"""
import os, sys
import logging
from BeautifulSoup import BeautifulSoup, Tag, NavigableString, Comment
from path import path
import subprocess
from PIL import Image
import cgi, cgitb
sys.stderr = sys.stdout
cgitb.enable(display=True)
 
class Cvt():
    def __init__(self, soup):
        self.soup = soup
        self.processlist = [2,3]
        self.methods = { 1:self.method_1, 2:self.method_2, 3:self.method_3, 4:self.method_4, 5:self.method_5,
                6:self.method_6, 7:self.method_7, 8:self.method_8, 9:self.method_9, 10:self.method_10, 
                11:self.method_11, 12:self.method_12, 13:self.method_13, 14:self.method_14, 15:self.method_15,
                16:self.method_16}


    def method_1(self):
        link = Tag(self.soup, 'link')
        link['rel']="StyleSheet"
        link['type']="text/css"
        link['href']="../../css/activity.css"
        meta = self.soup.find('meta')
        meta.insert(0,link)
    
    
    def method_2(self):
        tblkeys = ['width', 'border', 'bordercolor', 'cellpadding', 'cellspacing', 'frame', 'rules', 'dir']
        tbls = self.soup.findAll('table')
        for tbl in tbls:
            subtbls = tbl.findAll('table')
            for subtbl in subtbls:
                ps = subtbl.findAll('p')
                for p in ps:
                    if p.find('b'):
                        subtbl.replaceWith(p)
        tbls = self.soup.findAll('table')
        for tbl in tbls:
            for key in tblkeys:
                try:
                    del tbl[key]
                except:
                    pass
    
    
    def method_3(self):
        tdkeys = ['width', 'height', 'bgcolor', 'valign']
        tds = self.soup.findAll('td')
        for td in tds:
            for key in tdkeys:
                try:
                    del td[key]
                except:
                    pass
    
    
    def method_4(self):
        pkeys=['lang', 'align', 'style', 'class']
        ps = self.soup.findAll('p')
        for p in ps:
            for key in pkeys:
                centerflag = False
                try:
                    if 'head' in p['class']:
                        centerflag = True
                except:
                    pass
                try:
                    del p[key]
                except:
                    pass
            if centerflag:
                p['class'] = 'center'
    
    
    def method_5(self):
        pkeys=['lang', 'align', 'style', 'class']
        ps = self.soup.findAll('h1')
        for p in ps:
            for key in pkeys:
               try:
                   del p[key]
               except:
                   pass
    
    
    def method_6(self):
        pkeys=['lang', 'align', 'style', 'class']
        ps = self.soup.findAll('h2')
        for p in ps:
            for key in pkeys:
                try:
                    del p[key]
                except:
                    pass
            p['class']='center'
        
    

    
    def method_7(self):
        pkeys=['lang', 'align', 'style', 'class']
        ps = self.soup.findAll('h3')
        for p in ps:
            for key in pkeys:
                try:
                    del p[key]
                except:
                    pass
            p['class']='center'
    
    
    def method_8(self):
        ps = self.soup.findAll('p')
        for p in ps:
            bs = p.findAll('b')
            for b in bs:
                try:
                    if 'LO' in b.string:
                        if p.findParents('h1'):
                            h1=p.findParent('h1')
                            h1.replaceWith('<p class="solid">' + str(b) + '</p>')
                        else:
                            p.replaceWith('<p class="solid">' + str(b) + '</p>')
                except:
                    print 'b string not found', b.prettify()
    
    
    def method_9(self):
        done = False
        while not done:
            done=True
            fs = self.soup.findAll('font')
            for font in fs:
                if font.string:
                    font.parent.insert(0,font.string)
                    font.extract()
                    done = False
                if font.find('b'):
                    font.parent.insert(0,font.find('b'))
                    font.extract()
                    done=False
    
    
    def method_10(self):
        tbls=self.soup.findAll('table')
        count=0
        for tbl in tbls:
            if count > 0:
                tbl['class'] = 'border'
                tds = tbl.findAll('td')
                for td in tds:
                    td['class']='border'
                ths = tbl.findAll('th')
                for th in ths:
                    th['class']='border'
            else:
                td = tbl.find('td')
                td['class']='top'
                 
            count += 1
            h1s = tbl.findAll('h1')
            for h1 in h1s:
                cs = h1.contents
                newc = ''
                for c in cs:
                    if str(c).find('Activity') > -1:
                        c = '<h3>' + str(c) + '</h3>'
                    newc = newc + str(c)                        
                h1.replaceWith(newc)
            collst = [10,20,25,30,33,40,50,60,67,70,75,80,90]
            cols = tbl.findAll('col')
            if len(cols) < 2:
                continue
            widths = []
            sumw = 0
            for col in cols:
                try:
                    w = col['width']
                except:
                    w = str(0)
                w = w.replace('*','')
                widths.append(int(w))
                sumw = sumw + int(w)
            if sumw > 0:
                colws = []
                for width in widths:
                    percent = (100*width) / sumw
                    ix = 0
                    if percent > 90:
                        percent = 90
                    while ix < len(collst) and percent > collst[ix]:
                        ix += 1
                    try:
                        if not percent==collst[ix] and ix>1 and percent<=collst[ix-1]+((collst[ix-1]+collst[ix])/2):
                            ix -= 1
                    except:
                        print 'method_10: out of range', percent, width, sumw
                    colws.append(collst[ix])
                total = 0
                for colw in range(len(colws)-1):
                    total = total + colws[colw]
                colw = 100-total
                ix = 0
                while ix < len(collst) and colw > collst[ix]:
                    ix+=1
                if ix > 1:
                    colws[len(colws)-1] = collst[ix-1]
                else:
                    colws[len(colws)-1] = collst[0]
                count = 0
                for col in cols:
                    col['class'] = 'col_' + str(colws[count])
                    del col['width']
                    count += 1
            trs = tbl.findAll('tr')
            count = 0
            for tr in trs:
                count += 1
                tds = tr.findAll('td')
                for td in tds:
                    try:
                        st = td['class']
                    except:
                        st = ""
                    if count == 1:
                        td['class']=st + ' head'
                    elif count == 2:
                        td['class']=st + ' subhead'   
    
    
    def method_11(self):
        ps = self.soup.findAll('p')
        for p in ps:
            tgs = p.findAll(True)
            if len(tgs) == 2 and len(p.findAll('img')) == 1:
                p.replaceWith(tgs[0])
            if len(tgs) == 1 and len(p.findAll('br')) == 1:
                p.replaceWith(tgs[0])         
    
    
    def method_12(self):
        spans = self.soup.findAll('span')
        for span in spans:
            t = span.find(True, recursive=False)
            try:
                span.replaceWith(t)
            except:
                pass
    
    
    def method_13(self):
        contents = self.soup.body.contents
        c = contents[0]
        if c.find('uNIT') > -1:
            c1 = c.replace('uNIT','UNIT')
            c2 = '<h1 class="center">' + c1 + '</h1>'
            self.soup.body.contents[0].replaceWith(c2)
    
    def method_14(self):
        skeys = ['style']
        spans = self.soup.findAll('span')
        for span in spans:
            for key in skeys:
                try:
                    del span[key]
                except:
                    pass
    
    def method_15(self):
        done = False
        while not done:
            done=True
            fs = self.soup.findAll('span')
            for f in fs:
                if f.string:
                    f.parent.insert(0,f.string)
                    f.extract()
                    done = False
        fs = self.soup.findAll('span')
        for f in fs:
            if f.string:
                print >>sys.stderr, f.string
                f.parent.insert(0,f.string)
                f.extract()

    def method_16(self):
        comments = soup.findAll(
            text=lambda text:isinstance(text,Comment))
        for c in comments:
            if str(c).find('crossword'):
                t = c.findNext('table')
                break
        t['class'] = 'crossword'
        cols = t.findAll('col')
        for col in cols:
            col.extract()
        trs = t.findAll('tr')
        for tr in trs:
            try:
                del tr['valign']
            except:
                pass
        tds = t.findAll('td')
        for td in tds:
            tg = Tag(self.soup, 'td')
            tg['class'] = 'crossword'
            if not td.text == '&nbsp;':
                tg.insert(0,td.text)               
            td.replaceWith(tg)

def makesoup(txtin):
        soup = BeautifulSoup(txtin) 
        return soup

#main 
#get parameters from form
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
f = form.getfirst('filename', default='none')
txt = form.getfirst('content', default='no text found')
#set up soup
soup = makesoup(txt)
#perform conversions
cvt = Cvt(soup)
for method in cvt.processlist:
    cvt.methods[method]()
#set up txt
txtout = cvt.soup.prettify()
print txtout
#return
