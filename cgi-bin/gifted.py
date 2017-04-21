#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

#script to convert string in Moodle gift format to string in jquizme format
#def gifted(src): 
#    return quiz
#src is string containing questions in Moodle gift format
#quiz is string  with questions in jquizme format

def strip_gift(txt):
    #This function preprocesses gift export file produced by Moo dle

    #keep only (1) the question id as the name of the question
    #          (2) the actual question and answer (in gift format)

    #do it here
    lines = txt.split('//')
    count = 0
    questions = []
    for line in lines:
        count += 1
        #find // question id
        pos1 = line.find(':') + 1
        pos2 = line.find('name')
        id = line[pos1:pos2].strip()
        try:
            if int(id) < 1:
                continue
        except:
            continue
        #find question
        pos1 = line.rfind('::') + 2
        gift = line[pos1:].replace('\n','')
        questions.append([id,gift])
    #done did it
    return questions

def parse_answer(txt):
    pos1 = txt.rfind('%')
    if pos1<0:
        pos1 = txt.rfind('=')
        if pos1 <0:
            pos1 = 0
    pos2 = txt.rfind('#')
    if pos2 < 0: 
        pos2 = len(txt)
    answer = txt[pos1+1:pos2]
    print txt, answer, pos1, pos2
    return answer

def gifted(txt):
    #first we need to eliminate extraneous information in file produced by Moodle
    txtout = ''
    questions = strip_gift(txt)
    #gift format example:300l - 20dal \= _____l{	=%100%100# }
    #learn format example:<!--Q:8km= ___ dam A:800dam-->
    if questions:
        for item in questions:
            id = item[0]
            question = item[1]
            #we need to isolate answer and question body
            pos1 = question.find('{')
            pos2 = question.find('}')
            answer = parse_answer(question[pos1+1:pos2])
            txtout = txtout +id + '. <!--' + id +' Q:' + question[:pos1]+' A:'+answer+'-->\n'
    return txtout

