#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path

vals1 = ['hundred','ten','one']
vals2 = ['tenths','hundredths','thousandths','ten-thousandths','hundred-thousandths','millionths']
vals  = ['trillion','billion','million','thousand','unit','','']


#script to insert tables in source.txt
#create markup in source.txt - python
#refresh Content Edit screen - javascript
log = open('/tmp/logInsert','w')
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
params = form.getfirst('params',default="{'cols':1}")
pth = form.getfirst('pth')
print >> log,pth,params
try:
    params = eval(params)
except:
    print >> log, 'eval failed',sys.exc_info()[:2]
else:
    print >> log, 'eval successful'
#create text to insert according to params
try:
    kind = params['kind']
    cols = params['cols']
    rows = params['rows']
    headers = params['headers']
    decimals = params['decimals']
except:
    print >> log,'get params failed',sys.exc_info()[:2]
else:
    print >> log,kind,cols,rows,headers,decimals
if kind == 3:
    nstr = cols
    n=int(nstr)
    if n<1:
        n = 1
    if n>10:
        n = 10
    print >> log, 'n',n
    htmlout = '<p>&nbsp;&nbsp;</p><table><tbody>\n'
    row1 = '<tr>11111</tr>'
    row2 = '<tr>22222</tr>'
    row3 = '<tr>33333</tr>'
    tds = '<td>999.9</td><td></td>'
    tdsum ="<td class='sum'>999.9</td><td></td>"
    fullrow = ''
    for i in range(n):
        fullrow = fullrow+tds
    fullrows = ''
    for i in range(n):
        fullrows = fullrows+tdsum
    htmlout = htmlout + row1.replace('11111',fullrow)+'\n'
    htmlout = htmlout + row2.replace('22222',fullrows)+'\n'
    htmlout = htmlout + row3.replace('33333',fullrow)+'\n'
    htmlout = htmlout + '</tbody></table>\n<p>&nbsp;&nbsp;</p>\n'
    insert = htmlout
elif kind==1: #normal table
    cell = '<td>data</td>'
    insert = '<p>&nbsp;&nbsp;</p><table>'
    if headers == 'Y':
        insert += '<thead>'
        for col in range(int(cols)):
            insert += '<th>title</th>'
        insert += '</thead>'
    insert += '<tbody>'
    for row in range(rows):
        insert += '<tr>'
        for col in range(cols):
            insert += cell
        insert += '</tr>'
    insert += '</tbody></table><p>&nbsp;&nbsp;</p>'
elif kind==2: #place table
    cell = "<td class='digit'>9</td>"
    decimal_point = "<td class='decimal_point'>.</td>"
    insert = '<p>&nbsp;&nbsp;</p><table><thead><tr>'
    #calculate count based on number of cols and decimals
    index = 4 - (cols-(decimals+1))/3
    print >> log, vals,cols,index         
    for col in range(cols):
        if col%3 == 1:
            print >> log, 'col',col,col%3,'index',index
       	    insert += "<th class='middle'>"+vals[index]+'</th>'
            index+=1
        else:
            if col%3 == 0:
               insert += "<th class='left'></th>"
            else:
               insert += "<th class='right'></th>"
    try:
        #insert second row of headers
        insert += '</tr><tr>'
        for col in range(cols-decimals):
            insert += '<th>'+vals1[col%3]+'</th>'
        if decimals > 0:
            insert += "<th class='middle'></th>"
        for col in range(decimals):
            insert += '<th>'+vals2[col]+'</th>'
        insert += '</tr></thead>' 
        insert += '<tbody>'
        print >> log, 'insert',insert
        for row in range(rows):
       	    insert += '<tr>'
       	    for col in range(cols-decimals):
                insert += cell
            if decimals > 0:
                insert += decimal_point
            for col in range(decimals):
                insert += cell
            insert += '</tr>'
        insert += '</tbody></table><p>&nbsp;&nbsp;</p>'
    except:
        print >> log, 'processing failed',sys.exc_info()[:2]
    else:
        print >> log, 'processing successful'
else:
    print >>log, 'incorrect value for kind',kind
    insert = ''
#append text to source.txt
txt = ''
try:
    fin = open(path(pth) / 'source.txt','r')
    txt = fin.read()
    fin.close()
except:
    print >> log, 'read source.txt failed',sys.exc_info()[:2]
if txt:
    txtout = txt+insert
else:
    txtout = ''
if txtout:
    try:
        fout = open(path(pth) / 'source.txt','w')
        fout.write(txtout)
        fout.close()
    except:
        print >> log,'rewrite source.txt failed',sys.exc_info()[:2]
    else:
        print >> log,'rewrite source.txt succeeded'
log.close()
