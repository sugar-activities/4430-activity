#!/usr/bin/python
# -*- coding:utf-8 -*-
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
        self.kstrongs = 0
        self.kspans = 0
        self.kfonts = 0
        #methods
        #method_2 - remove style attributes from table tags
        #method_3 - remove style attributes from td tags
        #method_4 - remove style attributes from p tags
        #method_5 - remove style attributes from tr tags
        #method_6 - remove col tags
        #method_9 - remove fonts retaining content
        #method_10 - remove empty p tags (string == '&nbsp;')
        #method_11 - remove spans retaining content
        #self.processlist = [2, 3, 4, 5, 6, 7, 9, 10, 11, 12]
        self.processlist = [13]
        self.methods = { 1:self.method_1, 2:self.method_2, 3:self.method_3, 4:self.method_4, 5:self.method_5,
                6:self.method_6, 7:self.method_7, 8:self.method_8, 9:self.method_9, 10:self.method_10, 
                11:self.method_11, 12:self.method_12, 13:self.method_13,
        }


    def method_1(self):
        link = Tag(self.soup, 'link')
        link['rel']="StyleSheet"
        link['type']="text/css"
        link['href']="../../css/activity.css"
        meta = self.soup.find('meta')
        meta.insert(0,link)
    
    #remove style attributes from table tags
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
    
    #remove style attributes from td tags
    def method_3(self):
        tdkeys = ['width', 'height', 'bgcolor', 'valign']
        tds = self.soup.findAll('td')
        for td in tds:
            for key in tdkeys:
                try:
                    del td[key]
                except:
                    pass
    
    #remove style attributes from p tags     
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
    
    #remove style attributes from tr tags
    def method_5(self):
        pkeys=['lang', 'align', 'style', 'class', 'valign']
        ps = self.soup.findAll('tr')
        for p in ps:
            for key in pkeys:
               try:
                   del p[key]
               except:
                   pass
    
    #remove col tags
    def method_6(self):
        cols = self.soup.findAll('col')
        for col in cols:
            col.extract()

    #remove attributes from span tags      
    def method_7(self):
        pkeys=['lang', 'align', 'style', 'class']
        ps = self.soup.findAll('span')
        for p in ps:
            for key in pkeys:
                try:
                    del p[key]
                except:
                    pass
    
    
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
    
    #remove font tags retaining content 
    def method_9(self):
        done = False
        while not done:
            fonts = self.soup.findAll('font')
            if len(fonts) > 0:
               fonts[0].parent.insert(0,fonts[0].extract().renderContents())
               self.kfonts += 1
            else:
               done=True

    #remove empty paragraphs (used for spacing)
    def method_10(self):
        done = False
        while not done: 
            done = True
            ps = self.soup.findAll('p')
            for p in ps:
                if p.string == '&nbsp;':
                    p.extract()
                    done = False
  
    #remove spans (replace with p tags) retaining content 
    def method_11(self):
        done = False
        while not done:
            spans = self.soup.findAll('span')
            if len(spans) > 0:
               spans[0].parent.insert(0,spans[0].extract().renderContents())
               self.kspans += 1
            else:
               done=True

    #remove strong tags retaining content 
    def method_12(self):
        done = False
        while not done:
            strongs = self.soup.findAll('strong')
            if len(strongs) > 0:
               strongs[0].parent.insert(0,strongs[0].extract().renderContents())
               self.kstrongs += 1
            else:
               done = True
    
    FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])

    def dumpString(self, src, length=16):
        result = []
        for i in xrange(0, len(src), length):
            chars=src[i:i+length]
            hex = ' '.join(["%02x" % ord(x) for x in chars])
            printable = ''.join(["%s" % ((ord(x) <=127 and self.FILTER[ord(x)]) or '.') for x in chars])
            result.append("%04x %-*s\n" % (i, length*3, hex, printable))
        return ''.join(result)

    def dumpUnicodeString(self, src, length=8):
        result = []
        for i in xrange(0, len(src), length):
            unichars = src[i:i+length]
            hex = ' '.join(["%04x" % ord(x) for x in unichars])
            printable = ''.join(["%s" % ((ord(x) <= 127 and self.FILTER[ord(x)]) or '.') for x in unichars])
            result.append("%04x %-*s %s\n" % (i*2, length*5, hex, printable))
        return ''.join(result)

    def dump(self, s):
        import types
        if type(s) == types.StringType:
            if len(s) > 0:
                return self.dumpString(s, length=len(s))
        elif type(s) == types.UnicodeType:
            if len(s) > 0:
                return self.dumpUnicodeString(s, length=len(s))

    def method_13(self):
        spans = self.soup.findAll('span')
        count = 0
        for span in spans:
            count += 1
            t = span['style']
            if t.find('Symbol') > -1:
                v = unicode(span.contents[0])
                w = ''
                for i in range(len(v)):
                    w = w + hex(ord(v[i])) + ' '
                print count,':','<p>', w,'</p>'
        txt = unicode(soup)
        txt1 = txt.replace(u'\uf0b8','*/*')
        txt2 = txt1.replace(u'\uf02d','*')
        txt3 = txt2.replace(u'\uf050', 'x')
        txt4 = txt3.replace(u'\uf072', 'x')
        txt5 = txt4.replace(u'\uf03d', '=')
        self.soup = BeautifulSoup(txt5.replace(u'\uf02b', '+'))

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
print 'spans', cvt.kspans, 'fonts', cvt.kfonts, 'strongs', cvt.kstrongs
print txtout
#return
