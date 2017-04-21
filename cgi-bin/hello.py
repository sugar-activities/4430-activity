#!/usr/bin/python
import cgi, cgitb

cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'

log = open('/tmp/logHello','w')
print >> log, 'Hello World!'
log.close()

