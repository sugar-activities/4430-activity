#!/usr/bin/python

import sys
import cgi, cgitb
import subprocess
from sugar.activity import activity
from activities import copyFile

sys.stderr = sys.stdout
cgitb.enable(display=True)

print 'Content-Type:text/html\n\n'
log = open('/tmp/logl','w')
print >>log,'launch log opened'
bundle_dir = activity.get_bundle_path()
form = cgi.FieldStorage()
activity = form.getfirst('activity', default='')
print >> log, 'launch', activity
if len(activity)>0:
    bundle = form.getfirst('bundle', default='')
    bundle_pth = bundle_dir + '/' + bundle
    #perform actions based on which activity 
    if activity == 'Wordsearch':
        copyFile(bundle_pth,'~/Activities/Wordsearch.activity/wordlist/sample.txt')
        cwd = '~/Activities/Wordsearch.activity'
        service_name = 'ch.tea.Wordsearch'
    elif activity == 'ShowNTell':
        fout = open('/tmp/showntell','w')
        fout.write(bundle_pth)
        fout.close()
        cwd = '~/Activities/ShowNTell.activity'
        service_name = 'org.laptop.showntell'
    elif activity == 'Quiz':
        fout = open('/tmp/quiz','w')
        fout.write(bundle_pth)
        fout.close()
        cwd = '~/Activities/Quiz.activity'
        service_name = 'org.laptop.Quiz'
    elif activity == 'Jukebox':
        fout = open('/tmp/jukebox','w')
        fout.write(bundle_pth)
        fout.close()
        cwd = '~/Activities/Jukebox.activity'
        service_name = 'org.laptop.sugar.Jukebox'
    print >>log,'launch activity',activity,'service name', service_name 
    print >>log,'bundle',  bundle, 'from', cwd
    subprocess.call('sugar-launch '+service_name,cwd=cwd,shell=True)
    print >>log,'sugar-launch'
else:
    print >> log, 'no activity'
log.close()
