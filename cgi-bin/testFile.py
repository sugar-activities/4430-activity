#!/usr/bin/python
import os, sys, subprocess
import shutil
import cgi, cgitb
from BeautifulSoup import BeautifulSoup
from path import path
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
log = open('/tmp/logTestFile','w')
form = cgi.FieldStorage()
print >> log, 'form', form
log.close()

