 #!/usr/bin/python
import sys, subprocess
from path import path
from BeautifulSoup import BeautifulSoup

KARMAPTH = path('content/karma')
truelist = ['{T}','{True}','{t}','{true}']

def scantxt(txt):
    screens = []
    pos = txt.find('<hr />')
    while pos > -1:
        screens.append(txt[:pos])
        txt = txt[pos+6:]
        pos = txt.find('<hr />')
    screens.append(txt)
    return screens

def addQuestion(questionstrings,questionstring):
    #delete leading ::xxxx::
    pos1 = questionstring.find('::')
    pos2 = questionstring.rfind('::')
    if pos1 < 0 or pos2 < 0:
        question = questionstring
    else:
        question = questionstring[:pos1]+questionstring[pos2+2:]
    questionstrings.append(question)
    return

def scanquiz(txt):
    global log
    quizmode = False
    lines = txt.split('\n')
    questionstrings = []
    questionstring = ''
    count = 0
    for line in lines:
        count += 1
        #print >> log, count, quizmode, line
        #use gift format
        #bracketed by /*Quiz and */
        #blank line separates questions
        if not quizmode:
            pos = line.find('<!--Quiz')
            if pos > -1:
                quizmode = True
        else:
            pos1 = line[pos:].find('-->')
            if pos1 > -1:
                quizmode = False
                if questionstring:
                    addQuestion(questionstrings,questionstring)
                    questionstring = ''
                continue
            if len(line)>1:
                questionstring += line
            elif questionstring:
                addQuestion(questionstrings,questionstring)
                questionstring = ''
    print >> log, 'questions found',len(questionstrings)
    return questionstrings

def makequiz(questionstrings):
    #process questions in gift format
    #find question and answer
    tf = ''
    mc = ''
    sa = ''
    for questionstring in questionstrings:
        pos1 = questionstring.find('{')
        if pos1 < 0:
            print >> log,'bad question',questionstring
            continue
        pos2 = questionstring.find('}')
        if pos2 < 0:
            print >> log,'bad question',questionstring
            continue
        question = '{ques: "' + questionstring[:pos1]+questionstring[pos2:-1] +'",'
        gift_answer = questionstring[pos1:pos2+1]
        if not '=' in gift_answer:
           q = question + ' ans:false},\n'
           for item in truelist:
               if item in gift_answer:
                   q = question + ' ans:true},\n'
                   break
           tf+= q
        else:
            if '~' in gift_answer: #multiple-choice
                #note correct answer must be first followed by distractors
                #find correct answer =
                pos1 = gift_answer.find('=')
                pos2 = gift_answer[pos1:].find('~')+pos1
                ans = gift_answer[pos1+1:pos2]
                #find distractors ~
                ansSel = gift_answer[pos2+1:-1].replace(' ~','", "')
                mc += question + '\nans:"'+ans+'",\nansSel:["'+ansSel+'"]},\n'
            else: #short answer or cloze
                #find correct answer =
                pos1 = gift_answer.find('=')
                ans = gift_answer[pos1+1:-1]
                sa += question + ' ans:"'+ans+'"},\n'
    quiztxt = ''
    if len(mc) > 0:
        quiztxt = quiztxt + ' multiList:[\n' + str(mc) + '],\n'
    if len(tf) > 0:
        quiztxt = quiztxt + ' tf:[\n' + str(tf) + '],\n'
    if len(sa) > 0:
        quiztxt = quiztxt + ' fill:[\n' + str(sa) + '],\n'
    print >> log,'questionstrings',len(questionstrings),questionstrings
    print >> log,'quiztxt',quiztxt
    return quiztxt

def process_images(txt):
    #process imagelist
    done = False
    imagelist = []
    while not done:
        pos1 = txt.find('<!--I')
        if pos1 < 0:
            done = True
            continue
        pos2 = txt[pos1:].find('-->')
        if pos2 < 0:
            done = True
            continue
        comment = txt[pos1:pos1+pos2+3]
        pos3 = comment.find('_')
        pos4 = comment.find('I')
        imgno = comment[pos4+1:pos3]
        if 'left' in comment:
            class_insert = "class='image_left'"
        elif 'right' in comment:
            class_insert = "class='image_right'"
        else:
            class_insert = ''
        insert = "<span id='I"+imgno+"' "+class_insert+"></span>\n"
        txt = txt[:pos1]+insert+txt[pos1+pos2+3:]
        imagelist.append(comment)
    return txt, imagelist

def process_audio(txt):
    done = False
    #process audiolist
    audiolist = []
    while not done:
        pos1 = txt.find('<!--A')
        if pos1 < 0:
            done=True
            continue
        pos2 = txt[pos1:].find('-->')
        comment = txt[pos1:pos1+pos2+3]
        txt = txt[:pos1]+txt[pos1+pos2+3:]
        audiolist.append(comment)
    return audiolist

def process_video(txt):
    #process videolist
    done = False
    videolist = []
    while not done:
        pos1 = txt.find('<!--V')
        if pos1 < 0:
            done = True
            continue
        pos2 = txt[pos1:].find('-->')
        if pos2 < 0:
            done = True
            continue
        comment = txt[pos1:pos1+pos2+3]
        pos3 = comment.find('_')
        pos4 = comment.find('V')
        imgno = comment[pos4+1:pos3]
        if 'left' in comment:
            class_insert = "class='image_left'"
        elif 'right' in comment:
            class_insert = "class='image_right'"
        else:
            class_insert = ''
        insert = "\n<span id='V"+imgno+"' "+class_insert+"></span>\n"
        txt = txt[:pos1]+txt[pos1+pos2+3:]+insert
        videolist.append(comment)
    return txt, videolist

def generate_image(imagelist):
    lessontxt = ''
    host = 'http://localhost:8008/'
    for image in imagelist:
        #parse string
        pos = image.find('I')
        pos1 = image.find('_')
        imgn = image[pos:pos1]
        pos3 = image[pos1:].find(' ')
        img = image[pos1+1:pos1+pos3]
        if 'right' in image:
            position = 'image_right'
        else:
            position = 'image_left' 
        #create lessontxt
        lessontxt = lessontxt + "         $('#"+imgn+"')\n"
        lessontxt = lessontxt + "           $('<img>',{\n"
        lessontxt = lessontxt + "             src:host+pth+'"+img+"'\n"
        lessontxt = lessontxt + "           })\n"
        lessontxt = lessontxt + "           .appendTo('#"+imgn+"')\n"
    return lessontxt

def generate_audio(audiolist):
    lessontxt = ''
    if audiolist:
        lessontxt += "$('#mediaPlay').show();\n"
    for clip in audiolist:
        #parse string <!--A1_name:file.ogg-->
        pos = clip.find('A')
        pos1 = clip.find('_')
        imgn = clip[pos:pos1]
        pos2 = clip[pos1:].find('.')
        clp = clip[pos1+1:pos1+pos2]
        print >> log, 'clp',clp,'from clip',clip
        pos4 = clp.find(':')
        if pos4 > -1:
            clp = clp[:pos4]
            print >> log, 'clip from pos4',clp
        #create lessontxt
        lessontxt = lessontxt + "$('#mediaPlay')\n"
        lessontxt = lessontxt + "    .click(function(){\n"
        lessontxt = lessontxt + "        playAudio(karma,'"+clp+"');\n"
        lessontxt = lessontxt + "    });\n"
       	lessontxt = lessontxt + "$('#mediaPause')\n"
       	lessontxt = lessontxt + "    .click(function(){\n"
       	lessontxt = lessontxt +	"      	 pauseAudio(karma,'"+clp+"');\n"
       	lessontxt = lessontxt +	"    });\n"
        print >> log,lessontxt
    return lessontxt

def generate_video(videolist):
    lessontxt = ''
    host = 'http://localhost:8008/'
    for video in videolist:
        print >> log, type(video),video
        #parse string
        pos = video.find('V')
        pos1 = video.find('_')
        vidn = video[pos:pos1]
        pos3 = video[pos1:].find(' ')
        if pos3 < 0:
            pos3 = video[pos1:].find('-->')
        vid = video[pos1+1:pos1+pos3]
        pos4 = vid.find(':')
        if pos4 > -1:
            vid = vid[:pos4]
        print >> log,video,pos1,pos3
        print >> log,'vid',len(vid),vid
        #create lessontxt
        lessontxt = ''
        lessontxt = lessontxt + "        karma.createVideo('"+vid+"')\n"
        lessontxt = lessontxt + "        .attr('controls','true')\n"
        lessontxt = lessontxt + "        .appendTo('#"+vidn+"')\n"
    return lessontxt

def generate_exercises(ex):
    lessontxt= "    $('#content')\n"
    lessontxt+= "      .load(host+'" + ex[1] + "');\n"
    return lessontxt

def generate_bundle(bundle):
    lessontxt=  "    $('<div id=" +'"txtSugar">' + "')\n"
    lessontxt+= "      .appendTo('#content')\n"
    lessontxt+= "      .load(host+'cgi-bin/sugarLaunch.py',\n"
    lessontxt+= "      {'activity':'" + bundle[0] + "',\n"
    lessontxt+= "      'bundle':pth+'" + bundle[1] + "',\n"
    lessontxt+= "      'mime':'" + bundle[2] + "'});\n"
    return lessontxt

def process_exercises(screen):
    ex=[]
    loc = screen.find('<!--EX:')
    if loc > -1:
        loc1 = screen[loc:].find('-->')
        txt = screen[loc+7:loc1]
        items = txt.split(',')
        for item in items:
            ex.append(item)
    return ex

def process_bundle(screen):
    bundle=[]
    loc = screen.find('<!--B:')
    if loc > -1:
        loc1 = screen[loc:].find(',')+loc
        loc2 = screen[loc1+1:].find(',')+loc1+1
        loc3 = screen[loc2:].find('-->')+loc2
        bundle = [screen[loc+6:loc1],screen[loc1+1:loc2],screen[loc2+1:loc3]]
    return bundle

def buildLesson(fpth):
    #rebuild a*.txt, quiz.js, and start.js in activity folder
    #first split into screens, then scan for quiz items, images, and audio clips
    global log
    log = open('/tmp/logLesson','w')
    try:
        print >> log,'in buildLesson',fpth
    except:
        help = open('/tmp/logHelp','w')
        print >> help,'log not open',sys.exc_info()[:2]
        help.close()
    added_links=[]
    added_scripts=[]
    ex = []
    bundle = []
    isKarma = False
    srcpth = fpth / 'source.txt'
    if srcpth.exists():
        fin = open(srcpth,'r')
        txtout = fin.read()
        fin.close()
        screens = scantxt(txtout)
    else:
        screens = []
    lessontxt = "host='http://localhost:8008/'\n"
    lessontxt = lessontxt + "pth='"+fpth+"/'\n"
    masterimagelist = []
    masteraudiolist = []
    mastervideolist = []
    if screens:
        if len(screens) < 2:
            nscreen = 0
        else: 
            nscreen = 1
        try:
            subprocess.call('rm -rf ' + fpth / 'a*.txt', shell = True)
        except:
            print >> log,'no a*.txt'
    else:
        nscreen = -1
    imagelists = []
    audiolists = []
    videolists = []
    print >> log, 'screens', len(screens)
    quiztxt = ''
    quiztxtout = ''
    audiolist = []
    videolist = []
    for screen in screens:
        screen, imagelist = process_images(screen)
        imagelists.append(imagelist)
        print >> log,'imagelist', len(imagelist)
        try: 
            for image in imagelist:
                masterimagelist.append(image)
            audiolist = process_audio(screen)
            audiolists.append(audiolist)
            for clip in audiolist:
                masteraudiolist.append(clip)
            try:
                screen, videolist = process_video(screen)
            except:
                print >> log, 'process_video failed',sys.exc_info()[:2]
            videolists.append(videolist)
            for clip in videolist:
                mastervideolist.append(clip)
            try:
                ex=process_exercises(screen)
            except:
                print >> log,'process_exercises failed',sys.exc_info()[:2]
            bundle=process_bundle(screen)
            questionstrings = scanquiz(screen)
        except:
            print >> log,'process failed',sys.exc_info()[:2]
        else:
            print >> log,'process succeeded'
        quiztxt = ''
        print >> log, 'questionstrings',len(questionstrings)
        if len(questionstrings)>0:
            try:
                quiztxt = makequiz(questionstrings)
            except:
                print >> log,'makequiz failed',sys.exc_info()[:2]
            else:
                print >> log,'quiztxt',len(quiztxt),quiztxt
        quiztxtout = ''
        if len(quiztxt) > 0:
            if nscreen > 0:
                quiztxtout='var quiz'+str(nscreen)+' ={\n'+quiztxt+'}\n'
            else: 
                quiztxtout = 'var quiz = {\n' + quiztxt + '}\n'
            opt = 'var options = {\n'
            opt = opt + '    random:false,\n'
            opt = opt + '    allRandom:false,\n'
            opt = opt + '    disableRestart:true,\n'
            opt = opt + '    disableDelete:true,\n'
            opt = opt + '    title: "Opportunity",}\n'
            quiztxtout = quiztxtout + opt
            print >> log,'quiztxtout',len(quiztxtout)
        if nscreen > 0:
            apth = fpth / 'a' + str(nscreen) + '.txt'
            nscreen += 1;
        else:
            apth = fpth / 'a.txt'
        if quiztxtout:
            screen ="<span id='quizArea'></span>\n" + screen
        fout = open(apth, 'w')
        fout.write(screen)
        fout.close()
    #rewrite start.js
    inits=['initialize','initLesson']
    starts=['startGame','initGame']
    alts=0
    lpth = fpth / 'lesson.js'
    if lpth.exists():
        fin=open(lpth,'r')
        txt=fin.read()
        fin.close()
        if 'startGame' in txt:
            alts=1
        added_scripts.append('lesson')
        added_scripts.append('flash')
    if nscreen < 1:
        lessontxt = lessontxt + "function "+inits[alts]+"(karma){\n"
        print >> log, 'srcpth',srcpth.exists(),srcpth
        if srcpth.exists():
            lessontxt = lessontxt + "   $('<div id = " + '"txtMain"/>' + "')\n"
            lessontxt = lessontxt + "       .appendTo('#content')\n"
            lessontxt = lessontxt + "       .load(host+'cgi-bin/getFile.py',\n"
            lessontxt = lessontxt + "       {'filename':pth+'a.txt'},\n"
            lessontxt = lessontxt + "       function(){\n"
            lessontxt = lessontxt + generate_image(imagelist)
            lessontxt = lessontxt + generate_video(videolist)
            lessontxt = lessontxt + generate_audio(audiolist)
            lessontxt = lessontxt + "    });\n"
        if quiztxt or alts>0 or ex or bundle:
            lessontxt = lessontxt + "    $('#linkPlayAgain')\n"
            lessontxt = lessontxt + "      .show();\n"
        if alts>0:
            lessontxt = lessontxt + "    initialize(karma);\n"
        lessontxt = lessontxt + "};\n"
        lessontxt = lessontxt + "function "+starts[alts]+"(karma) {\n"
        if quiztxt:
            lessontxt = lessontxt + "    $('#quizArea')\n"
            lessontxt = lessontxt + "        .jQuizMe(quiz, options)\n"
        if alts > 0:
            lessontxt = lessontxt + "    startGame(karma);\n"
        if ex:
            print >> log,'ex',len(ex),ex
            if ex[0] == 'KA':
                added_scripts.append('khan')
            try:
                lessontxt = lessontxt + generate_exercises(ex)
            except:
                print >> log,'generate_exercises failed',sys.exc_info()[:2]
            else:
                print >> log,'generate_exercises successful'
        if bundle:
            print >> log,'bundle',len(bundle),bundle
            lessontxt = lessontxt + generate_bundle(bundle) 
        lessontxt = lessontxt + "};\n"
        lessontxt = lessontxt + "setUpLesson("+inits[alts]+", "+starts[alts]+");\n"
    else:
        lessontxt = lessontxt + "var currentScreen;\n\n"
        for s in range(len(screens)):
            screen = screens[s]
            lessontxt = lessontxt + "function generateScreen" + str(s+1) + "(karma) {\n"
            lessontxt = lessontxt + "currentScreen = " + str(s+1) + '\n'
            lessontxt = lessontxt + "   $('<div id = " + '"txtMain"/>' + "')\n"
            lessontxt = lessontxt + "       .appendTo('#content')\n"
            lessontxt = lessontxt + "       .load(host+'cgi-bin/getFile.py',\n"
            lessontxt = lessontxt + "       {'filename':pth+'a" + str(s+1) + ".txt'},\n"
            lessontxt = lessontxt + "       function(){\n"
            lessontxt = lessontxt + generate_image(imagelists[s])
            lessontxt = lessontxt + generate_audio(audiolists[s])
            lessontxt = lessontxt + generate_video(videolists[s])
            lessontxt = lessontxt + "       })\n"
            lessontxt = lessontxt + "};\n"
        lessontxt = lessontxt + "function "+inits[alts]+"() {};\n"
        lessontxt = lessontxt + "function "+starts[alts]+"(karma){\n};\n\n"
        lessontxt = lessontxt + "setUpMultiScreenLesson([\n"
        for s in range(len(screens)):
            lessontxt = lessontxt + "    generateScreen" + str(s+1) + ",\n"
        lessontxt = lessontxt + "],"+inits[alts]+", "+starts[alts]+");\n"
    lpth = fpth / 'start.js'
    fout = open(lpth, 'w')
    fout.write(lessontxt)
    fout.close()

    #write quiz.js, if necessary
    print >> log,'quiztxtout',len(quiztxtout)
    if len(quiztxtout) > 0:
        added_links.append('jquizme')
        added_scripts.append('jquizme')
        added_scripts.append('quiz')
        qpth = fpth / 'quiz.js'
        fout = open(qpth,'w')
        fout.write(quiztxtout)
        fout.close()

    #write lesson.css, if necessary
    print >>log, 'master image list', len(masterimagelist)
    txtout = ''
    if quiztxtout:
        txtout += '#quizArea{\n'
        txtout += '    position:relative;\n'
        txtout += '    width:600px;\n'
        txtout += '    height:450px;\n'
        txtout += '    background:#ffdd77;\n'
        txtout += '    float:right;\n'
        txtout += '}\n\n'
    if len(masterimagelist) > 0:
        imgnumber = 0
        for image in masterimagelist:
            #parse
            pos = image.find('I')
            pos1 = image.find('_')
            #make sure images are numbered consecutively
            imgnumber += 1
            imgn = str(imgnumber)
            pos = image.find('height')+7
            pos1 = image[pos:].find(' ')
            if pos1 < 0:
                pos1 = image[pos:].find('-->')
            print >> log,'found height',image[pos:pos+pos1]
            try:
                height = str(int(image[pos:pos+pos1])+30)
            except:
                print >> log,'height exception',sys.exc_info()[:2]
            pos = image.find('width')+6
            pos1 = image[pos:].find(' ')
            if pos1 < 0:
                pos1 = image[pos:].find('-->')
            w = image[pos:pos+pos1]
            print >> log,'found width',pos,pos1,w
            if w:
       	       try:
                   width = str(int(w)+30)
       	       except:
       	           print >> log,'width  exception',sys.exc_info()[:2]
            #write txtout
            print >> log,'width',width,'height',height
            txtout = txtout+'#I'+imgn+'{height: '+height+'px; width: '+width+'px;}\n'
    #write file
    if txtout:
        pth = fpth / 'lesson.css'
        fout = open(pth,'w')
        fout.write(txtout)
        fout.close()

    #write  lesson-karma.js
    #name:file.ogg or name:file.ogv - if no ':' then file:file.ogg and file:file.ogv
    if not isKarma:
        print >> log, 'write lesson-karma', str(len(masterimagelist)), str(len(masteraudiolist))
        txtlk = "image: [\n"
        for img in masterimagelist:
            #parse
            pos1 = img.find('_')
            pos2 = img[pos1:].find('.')
            pos3 = img[pos1:].find(' ')
            imgn = img[pos1+1:pos1+pos2]
            imgf = img[pos1+1:pos1+pos3]
            print >> log, 'img',img,imgn,imgf
            txtlk = txtlk	+ "{name:'"+imgn+"', file:'"+imgf+"'},\n"
        txtlk = txtlk + "    ],\naudio: [\n"
        for clip in masteraudiolist:
            #parse
            pos1 = clip.find('_')
            pos2 = clip.find('.')
            pos3 = clip.find('-->')
            clp = clip[pos1+1:pos2]
            clpf = clip[pos1+1:pos3]
            pos4 = clpf.find(':')
            if pos4 > -1:
                clp = clpf[:pos4]
                clpf = clpf[pos4+1:]
            print >> log, 'clip',clip,clp,clpf
            txtlk = txtlk + "{name:'"+clp+"', file:'"+clpf+"'},\n"
        txtlk = txtlk + "    ],\nvideo: [\n"
        for clip in mastervideolist:
            pos1 = clip.find('_')
            pos2 = clip[pos1:].find('.')
            pos3 = clip[pos1:].find(' ')
            if pos3<0:
                pos3 = clip[pos1:].find('-->')
            clp = clip[pos1+1:pos1+pos2]
            clpf = clip[pos1+1:pos1+pos3]
            print >> log,'clpf',clpf
            pos4 = clpf.find(':')
       	    if pos4	> -1:
       	        clp  = clpf[:pos4]
       	        clpf = clpf[pos4+1:]
                print >> log,'found pos4','clip',clip,'clp',clp,'clpf',clpf
            print >> log, 'clip',clip,'clp',clp,'clpf',clpf
            txtlk = txtlk + "{name:'"+clp+"', file:'"+clpf+"'},\n"
        txtlk = txtlk + "    ],\n"
        txtlk = '    return Karma({\n' +txtlk
        txtlk = 'function lesson_karma() {\n' + txtlk
        txtlk = txtlk + '                 });\n}\n'
        #write file
        pth = fpth / 'lesson-karma.js'
        lesson_pth = fpth / 'lesson.js'
        if not lesson_pth.exists() or not pth.exists():
            fout = open(pth,'w')
            fout.write(txtlk)
            fout.close()
    log.close()
    return added_links,added_scripts
