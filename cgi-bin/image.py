#!/usr/bin/python
import os, sys, subprocess
import cgi, cgitb
from path import path
from sugar.datastore import datastore
from BeautifulSoup import BeautifulSoup

base = path('../../Documents')
workarea = path('workarea')
subprocess.call('mkdir -p' + workarea,shell=True)

mime_types = ['image/bmp','image/gif','image/jpeg','image/png','image/tiff']
exts = ['.bmp','.gif','.jpg','.png','.tiff']

#script to insert image in activity
#list images in Journal or ~/Documents -python returns list
#user selects image - javascript
#show mock up of screens - javascript
#user selects screen - javascript
#copy converted and resized image to activity folder - python
#create markup in source.txt - python
#refresh Content Edit screen - javascript

def findScreen(screen, txt):
    n = int(screen)-1
    positions = []
    pos = 0
    done = False
    while not done:
        positions.append(pos)
        pos1 = txt[pos:].find('<hr />')
        if pos1 < 0:
            done = True
        else:
            pos = pos + pos1 + 6
    print >> log,'n',n,'positions',len(positions),positions
    if n < len(positions):
        return positions[n]
    else:
        return -1

cgitb.enable(display=True)
print 'Content-Type:text/html\n\n'
form = cgi.FieldStorage()
img = form.getfirst('image')
pth = path(form.getfirst('pth'))
width = form.getfirst('width',default='400')
height = form.getfirst('height',default='300')
#screen is '1' or '1L' or '1R' - accept upper or lower case.
#if float L - left, if R - float right else no float
screen_code = form.getfirst('screen',default='1').lower()
screen = screen_code
ok = form.getfirst('ok',default='')
log = open('/tmp/logImage','w')
print >> log, 'form',img,pth,width,height,screen,ok
log.close()
log = open('/tmp/logImage1','w')
if ok == 'ok':
    print >> log,'ok=ok'
    #user has accepted image with width and height
    screen = screen_code
    position = ''
    if 'l' in screen_code:
        position = 'left'
        screen = screen_code.replace('l','')
    if 'r' in screen_code:
        position = 'right'
        screen = screen_code.replace('r','')
    #resize image and copy to activity
    try:
        srcpth = path(img)
        dstpth = path(pth) / path(img).name
        cmd = 'convert -scale '+width+'x'+height+' '+srcpth+' '+dstpth
    except:
        print >> log,'prepare convert failed',sys.exc_info()[:2]
    else:
        print >> log, cmd
    try:
        subprocess.call(cmd,shell=True)
    except:
        print >> log, 'convert failed',sys.exc_info()[:2]
    else:
        print >> log, 'convert successful'
    #update source.txt
    log.close()
    log = open('/tmp/logImage2','w')
    fin = open(pth / 'source.txt','r')
    txt = fin.read()
    fin.close()
    print >> log,'source.txt',len(txt)
    print >> log,'update source.txt'
    log.close()
    log = open('/tmp/logImage3','w')
    if screen:
        pos = findScreen(screen,txt)
        if pos < 0:
            pos = 0
    else:
       pos = 0
    #buildLesson will assign proper image number
    print >> log, 'screen',screen,'pos',pos
    log.close()
    log = open('/tmp/image4','w')
    txtins = '\n<!--I1_'+srcpth.name +' width '
    txtins = txtins + width +' height '+ height +' '+position+'-->\n'
    txtout = txt[:pos]+txtins+txt[pos:]
    print >> log,txtins
    log.close()
    log=open('/tmp/logImage5','w')
    fout =  open(pth / 'source.txt','w')
    fout.write(txtout)
    fout.close()
elif img:
    #user has selected image - show thumbnail to get size,screen
    imgpth = path('workarea') / img
    temp = imgpth.namebase + '_thumb.png'
    thumbpth = path('workarea') / temp
    print >> log, 'selected image',img, thumbpth
    #show thumb to user, ask for size
    tpth = str(thumbpth)
    ipth = str(imgpth)
    rpth = str(pth)
    w='200'
    h='150'
    s=''
    print tpth+','+ipth+','+rpth+','+w+','+h+','+s
else: #return list of images - one per line
    #first clear workarea
    subprocess.call('rm -rf '+workarea+'/*',shell=True)
    #for each item in the datastore
    ds_objects, num_objects = datastore.find({},properties=['uid','title','mime_type'])
    print >> log, 'datastore',num_objects
    for i in xrange(0,num_objects,1):
        title = ds_objects[i].metadata['title']
        mime = ds_objects[i].metadata['mime_type']
        #if item is an image
        if mime in mime_types:
            #copy clip to workarea
            clip = path(ds_objects[i].get_file_path())
            dpth = workarea / title+clip.ext
            if not dpth.exists():
                cmd = 'cp ' + clip + ' ' + dpth
                #print >> log, cmd
                subprocess.call(cmd,shell=True)
    #copy each image in ~/Documents to workarea
    images = base.files()
    for image in images:
        if image.ext in exts:
            cmd = 'cp ' + image + ' ' + workarea
            #print >> log, cmd
            subprocess.call(cmd,shell=True)
    #display thumbnail of each in base folder
    images = workarea.files()
    print >> log, 'images',len(images)
    for image in images:
        if not 'thumb' in image:
            dst = workarea / image.namebase+'_thumb.png'
            cmd = 'convert -scale 150x150 ' + image +' '+dst
            #print >> log, cmd
            subprocess.call(cmd,shell=True)
    images = workarea.files('*_thumb.png')
    print >> log, 'thumbs', len(images)
    count = 0
    line = "<div id = 'thumbs'><table><tr>"
    print line
    print >> log,line
    for image in images:
        img_name = str(image.name).replace('_thumb','')
        img_path = path(image)
        img_title = img_path.namebase
        img_path = pth / img_path.name
        thumb_pth = base / image.name
        thmbkin = (image.namebase).replace('_thumb','')
        html="<td class='thumb' id="+thmbkin+" onclick=manageImage('"+img_name+"','"+pth+"');>"
        html=html+"<figure id="+img_title.replace('_thumb','')+">"
        html=html+"<img src=workarea/"+image.name+">"
        html=html+"<figcaption>"+thmbkin
        html=html+"</figcaption></figure></td>"
        print html
        print >> log, html
        count +=1
        if count == (count / 4)*4:
            print '</tr><tr>'
            print >> log, '</tr></tr>'
    print '</table></div>'
    print >> log,'</table></div>'
print >> log,'done'
log.close()
