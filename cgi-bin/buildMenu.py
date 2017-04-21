#!/usr/bin/python

#build index.html for a specified level

#
def buildMenu(levelName,added_links=[],added_scripts=[]):
#return a string 'index.html' which is generic for the corresponding level
#the calling script can add additional optional scripts as required
#linkList is a list of lists, one list per level
#ScriptList is a list of lists, one list per level
#the path to the scripts and css files in karma need to be adjusted based on the level
#path to scripts not in karma are in the same folder as the index.html file 

    log=open('/tmp/logMenu','w')
    print >> log,'buildMenu',levelName
    print >> log,'addl',len(added_links),added_links
    print >> log,'adds',len(added_scripts),added_scripts

    LEVELS = {'subject':0, 'course':1, 'unit':2, 'lesson':3, 'activity':4}
    PREFIXES = ['./','../','../../','../../../','../../../../']
    HEAD = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8"/><meta http-equiv="Pragma" content="no-cache"/>'   
    FOOT = '</head>\n<body>\n<div id="header"></div>\n'
    FOOT = FOOT + '<div id = "content"></div>\n'
    FOOT = FOOT + '<div id = "footer"></div>\n</body>\n</html>\n'
    LINKS = {}
    LINKS['menu'] = 'karma/css/menu.css'
    LINKS['global'] = 'karma/css/global.css'
    LINKS['jquizme'] = 'karma/css/jquizme.css'
    LINKS['lesson'] = 'lesson.css'
    LINKS['crossword'] = 'crossword.css'
    LINKS['hangman'] = 'hangman.css'
    LINKS['identification'] = 'identification.css'
    LINKS['mad-libs'] = 'mad-libs.css'
    LINKS['matching'] = 'matching.css'
    LINKS['matching-pairs'] = 'matching-pairs.css'
    LINKS['multiple-choice-sentences'] = 'multiple-choice-sentences.css'
    LINKS['vocabulary-with-game'] = 'vocabulary-with-game.css'
    LINKS['what-is-this'] = 'what-is-this.css'
    LINKS['anagrams'] = 'anagrams'
    priorityLinks = ['menu','global','jquizme','crossword',
                     'hangman','identification','mad-libs','matching',
                     'matching-pairs','multiple-choice-sentences',
                     'vocabulary-with-game','what-is-this','anagrams','lesson']
    SCRIPTS = {}
    SCRIPTS['jquery'] = 'karma/js/external/jquery-1.4.2.js'
    SCRIPTS['ui'] = 'karma/js/external/jquery-ui-1.8.2.js'
    SCRIPTS['flash'] =  'karma/js/flash.js'
    SCRIPTS['karma'] = "karma/js/karma.js"
    SCRIPTS['common'] = "karma/js/common.js"
    SCRIPTS['clickable'] = "karma/js/jquery.clickable.js"
    SCRIPTS['i18n'] = "karma/js/jquery.i18n.js"
    SCRIPTS['jquizme'] = "karma/js/jquizme.js"
    SCRIPTS['math'] = "karma/js/math.js"
    SCRIPTS['global'] = "karma/js/global.js"
    SCRIPTS['templates']="karma/templates/templates.js"
    SCRIPTS['edit'] = "karma/js/edit.js"
    SCRIPTS['subjects'] = "-0subjects.js"
    SCRIPTS['main'] = "karma/js/main.js"
    SCRIPTS['course'] = "karma/js/course.js"
    SCRIPTS['unit'] = "karma/js/unit.js"
    SCRIPTS['clock'] = 'karma/js/clock.js'
    SCRIPTS['lessons'] = "karma/js/lesson.js"
    SCRIPTS['lesson'] = "lesson.js"
    SCRIPTS['base'] = 'karma/js/base.js'
    SCRIPTS['milestones'] = "milestones.js"
    SCRIPTS['activities'] = "activities.js"
    SCRIPTS['lesson-karma'] =  "lesson-karma.js"
    SCRIPTS['courses'] = "-1courses.js"
    SCRIPTS['course'] = "karma/js/course.js"
    SCRIPTS['quiz']="quiz.js"
    SCRIPTS['khan']="khan/khan-exercise.js"
    SCRIPTS['ui.scoreboard'] = 'karma/js/ui.scoreboard.js'
    SCRIPTS['crossword']="crossword.js"
    SCRIPTS['hangman']="hangman.js"
    SCRIPTS['multiple-choice'] = 'karma/js/multiple-choice.js'
    SCRIPTS['identification'] = 'identification.js'
    SCRIPTS['configuration'] = 'configuration.js'
    SCRIPTS['mad-libs'] = 'mad-libs.js'
    SCRIPTS['objects'] = 'objects.js'
    SCRIPTS['matching'] = 'matching.js'
    SCRIPTS['matching-pairs'] = 'matching-pairs.js'
    SCRIPTS['multiple-choice-sentences'] = 'multiple-choice-sentences.js'
    SCRIPTS['label-generator'] = 'label-generator.js'
    SCRIPTS['init'] = 'init.js'
    SCRIPTS['addition'] = 'addition.js'
    SCRIPTS['quick'] = 'quick.js'
    SCRIPTS['vocabulary-with-game'] = 'vocabulary-with-game.js'
    SCRIPTS['what-is-this'] = 'what-is-this.js'
    SCRIPTS['anagrams'] = 'anagrams.js'
    SCRIPTS['start'] =  "start.js"
    priorityScripts = ['jquery','ui','flash','karma','common','clickable',
                       'i18n','jquizme','math','global','templates','edit','subjects',
                       'main','course','unit','lessons','base','lesson','milestones',
                       'activities','clock','lesson-karma','courses',
                       'quiz','khan','ui.scoreboard','multiple-choice',
                       'crossword','hangman','identification','configuration','mad-libs',
                       'objects','matching','matching-pairs','multiple-choice-sentences',
                       'addition.js','quick.js','init.js','vocabulary-with-game',
                       'label-generator','what-is-this','anagrams','start']
    linkPrefix = '<link rel="stylesheet" href="'
    linkPostfix ='" type="text/css"/>'
    scriptPrefix = '<script type="text/javascript" src="'
    scriptPostfix = '"></script>'
    linkList = [
                   ['menu'],
                   ['menu','global'],
                   ['global'],
                   ['global'],
                   ['global', 'lesson'],
               ]
    scriptList = [
                   ['jquery','ui','karma','clickable','i18n','subjects','main'],
                   ['jquery','ui','karma','clickable','i18n','subjects','courses','course'],
                   ['jquery','karma','global','edit','subjects','courses','milestones','unit'],
                   ['jquery','ui','karma','global','templates','edit','subjects',
                    'courses','activities', 'lessons'],
                   ['jquery','ui','karma','common','clickable',
                    'i18n','global','templates','edit','subjects','base','lesson-karma',
                    'start'],
                 ]

    links = ''
    lnks=[]
    level = LEVELS[levelName]
    for link in priorityLinks:
        if link in linkList[level] or link in added_links:
            lnks.append(link)
    for link in lnks:
        if 'karma' in LINKS[link]:
            pth = PREFIXES[level]+LINKS[link]
        else:
            pth = LINKS[link]
        links = links + linkPrefix + pth + linkPostfix + '\n'
    scrpts = []
    for script in priorityScripts:
        if script in scriptList[level] or script in added_scripts:
            scrpts.append(script)
    print >> log,'scrpts',len(scrpts),scrpts
    scripts = ''
    for script in scrpts:
        if 'karma' in SCRIPTS[script] and not script == 'lesson-karma':
            pth = PREFIXES[level]+SCRIPTS[script]
        else:
            pth = SCRIPTS[script]
            if '-0' in pth:
                pth = PREFIXES[level]+SCRIPTS[script].replace('-0','')
            elif '-1' in pth:
                pth = PREFIXES[level-1]+SCRIPTS[script].replace('-1','')
        scripts = scripts + scriptPrefix + pth + scriptPostfix +  '\n'
 
    txtout = HEAD + links + scripts + FOOT
    print >> log, 'done'
    print >> log, txtout
    log.close()
    return txtout
