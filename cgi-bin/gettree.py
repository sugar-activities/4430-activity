#!/usr/bin/env python

import sys
import cgi, cgitb
from path import path
from BeautifulSoup import BeautifulSoup
#script to return filetree
global n
global treelist
global txt
n=0
global flag
flag = False

def outTree(treelist, n):
    #prints files and folders in this folder
    basepath = treelist[n]
    txt = '<li class="closed"><span class = "folder">' + str(treelist[n]) + ' </span><ul id="folder">'
    #handle files and folders in this folder
    done = False
    n += 1
    while not done and n < len(treelist):
        if treelist[n].isdir():
            if len(treelist[n].splitall()) > len(basepath.splitall()):
                newtxt, n = outTree(treelist, n)
                txt = txt + newtxt
            else:
                done = 'True'
                txt = txt + '</ul></li>'
        else:
            fn = str(treelist[n])
            tmp = '<a href="javascript:ajaxLoad(' + "'" +  str(treelist[n]) + "'" +  ')">' + fn
            txt = txt + '<li><span class="file">' + tmp + '</a></span></li>'
            n += 1
    return txt, n

print 'Content-Type:text/html\n\n'
txt = ""
d = path('/media/2011/courseware')
treelist = []
level = 0
stack = []
if d.isdir():
    tree = d.walk()
    count = 0
    for itm in tree:
        flag = itm.isdir() and (itm.name =='English' or itm.name=='Mathematics')
        if flag or itm.ext == '.txt':
            count+=1
            treelist.append(itm)
treelist.sort()
n = 0
while n + 1 < len(treelist):
    newtxt, n = outTree(treelist,n)
    txt = txt + newtxt[:-1]

if len(txt) > 0:
    soup = BeautifulSoup(txt)
    txtout = soup.prettify()
    print txtout
