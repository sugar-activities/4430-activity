#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import cgi, cgitb
cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
txt = form.getfirst('text', default='I have nothing to say.')
subprocess.call('espeak ' + txt, shell=True)
