# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 19:35:27 2017
@author: ruben
"""
import logging
from .counter import countSampa
from .counter import countEmotions

class naf:
    def __init__(self,f,th=0.5):
        import xml.etree.ElementTree as et

        self.debug = logging.getLogger('debugLog')
        self.stdout  = logging.getLogger('stdoutLog')

        self.tree  = et.parse(f)
        self.root  = self.tree.getroot()

        self.debug.debug("reading words from {0}".format(f))
        self.WordList  = [word(i)  for i in self.root.find('text').findall('wf')]
        self.debug.debug("reading lemmas from {0}".format(f))
        self.lemmas = [lemma(i) for i in self.root.find('terms')]
        self.debug.debug("reading emotions from {0}".format(f))
        self.emolist= [emotions(i,th) for i in self.root.find('emotions') if i.tag == 'emotion']

        self.debug.debug("initialising counters")
        self.countSampa = countSampa()
        self.countEmotions = countEmotions()

        lemmaByID={i.TargetID():i for i in self.lemmas}
        emolistByID={j:i for i in self.emolist for j in i.ID()}

        for i in self.WordList:
            if i.WordID() in lemmaByID.keys():
                self.debug.debug("adding lemma for {0}".format(i.Word()))
                i.addLemma(lemmaByID[i.WordID()])
            if i.LemmaID() in  emolistByID.keys():
                self.debug.debug("adding emotions for {0}".format(i.Word()))
                i.addEmotions(emolistByID[i.LemmaID()])

    def translate(self,a):
        self.debug.debug("translating all words")
        self.translations="source, translation\n"
        for i in self.WordList:
            if i.isNotPunctuation():
                sampa=a.translate(i.Word())
                i.addSampa(sampa)
                self.translations+=i.Word()+", "+sampa+"\n"
        return self.translations

    def doCount(self,countSampa=True,countClusters=True,countEmotions=True):
        self.debug.debug("counting sampa, emotions and/or clusters")
        for i in self.WordList:
            if countSampa and i.Sampa():
                self.countSampa.add(i.Sampa())
            if (countEmotions or countClusters) and i.EmotionList():
                if countEmotions:
                    for j in i.EmotionList().Emotion():
                        self.countEmotions.addEmotion(j.Reference())
                if countClusters:
                    for j in i.EmotionList().Cluster():
                        self.countEmotions.addCluster(j.Reference())



    def get_wordlist(self, RemovePunctuation=True):
        if RemovePunctuation:
            return [i.Word() for i in self.WordList if i.isNotPunctuation()]
        return [i.Word() for i in self.WordList]

class emotion:
    def __init__(self,e):
        self.posnegClass={
            'love':'pos',
            'joy':'pos',
            'desire':'pos',
            'hope':'pos',
            'compassion':'pos',
            'happiness':'pos',
            'honor':'pos',
            'loyalty':'pos',
            'wonder':'pos',
            'moved':'pos',
            'aquiescence':'pos',
            'benevolence':'pos',
            'pride':'pos',
            'dedication':'pos',
            'trust':'pos',
            'awe':'pos',
            'relief':'pos',
            'sadness':'neg',
            'fear':'neg',
            'anger':'neg',
            'despair':'neg',
            'vindictiveness':'neg',
            'hatred':'neg',
            'remorse':'neg',
            'worry':'neg',
            'shame':'neg',
            'heavyHeartedness':'neg',
            'disgust':'neg',
            'spitefulness':'neg',
            'annoyance':'neg',
            'envy':'neg',
            'suspicion':'neg',
            'offended':'neg',
            'unhappiness':'neg',
            'dissapointment':'neg',
            'greed':'neg',
            'loss':'neg',
            'other': 'other'
        }
        self.properties={
            'confidence':float(e.attrib['confidence']),
            'reference':e.attrib['reference'].split(':')[1],
            'pos/neg':self.posnegClass[e.attrib['reference'].split(':')[1]]
        }
    def Confidence(self):
        return self.properties['confidence']
    def Reference(self):
        return self.properties['reference']
    def PosNeg(self):
        return self.properties['pos/neg']

class emotion_clsuter:
    def __init__(self,c):
        self.posnegClass={
            'sadness':'neg',
            'love':'pos',
            'anger':'neg',
            'fear':'neg',
            'joy':'pos',
            'desire':'pos',
            'despair':'neg',
            'disgust':'neg',
            'posSentiments':'pos',
            'compassion':'pos',
            'prideHonour':'pos',
            'other':'other'
        }
        self.properties={
            'confidence':float(c.attrib['confidence']),
            'reference':c.attrib['reference'],
            'pos/neg':self.posnegClass[c.attrib['reference']]
        }
    def Confidence(self):
        return self.properties['confidence']
    def Reference(self):
        return self.properties['reference']
    def PosNeg(self):
        return self.properties['pos/neg']

class emotions:
    def __init__(self,e,th=0.5):
        self.properties={
            'ID':[],
            'threshold':th,
            'emotions':[],
            'clusters':[]
        }

        for i in e.find('span'):
            self.properties['ID'].append(i.attrib['id'])
        for i in e.find('externalReferences'):
            if i.attrib['resource'] == 'heem:clusters':
                self.properties['clusters'].append(emotion_clsuter(i))
            elif i.attrib['resource']=='heem' and i.attrib['reference'].split(':')[0]=='emotionType':
                self.properties['emotions'].append(emotion(i))
    def setThreshold(self,th):
        self.properties['threshold']=th
    def ID(self):
        return self.properties['ID']
    def Emotion(self):
        return [i for i in self.properties['emotions'] if i.Confidence()>= self.properties['threshold']]
    def Cluster(self):
        return [i for i in self.properties['clusters'] if i.Confidence()>= self.properties['threshold']]

class lemma:
    def __init__(self,t):
        self.properties ={
            'ID':t.attrib['id'],
            'lemma':t.attrib['lemma'],
            'pos':t.attrib['pos'],
            'type':t.attrib['type'],
            'targetID':t.find('span').find('target').attrib['id']
        }
    def TargetID(self):
        return self.properties['targetID']
    def ID(self):
        return self.properties['ID']
    def Lemma(self):
        return self.properties['lemma']
    def Pos(self):
        return self.properties['pos']

class word:
    def __init__(self,w):
        self.properties={
            'word':w.text,
            'ID':w.attrib['id'],
            'length': int(w.attrib['length']),
            'offset': int(w.attrib['offset']),
            'sentence': int(w.attrib['sent']),
            'punctuation':[',', ';', '.', '?', "'", '!' '‘', '&', '-',':'],
            'lemma':None,
            'lemmaID':None,
            'emotions':None,
            'sampa':None
        }
    def isNotPunctuation(self):
        if self.properties['word'] in self.properties['punctuation']:
            return False
        return True
    def addLemma(self,l):
        self.properties['lemma']=l
        self.properties['lemmaID']=l.ID()
    def addEmotions(self,e):
        self.properties['emotions']=e
    def addSampa(self,s):
        self.properties['sampa']=s
    def Word(self):
        return self.properties['word']
    def WordID(self):
        return self.properties['ID']
    def EmotionList(self):
        return self.properties['emotions']
    def Lemma(self):
        return self.properties['lemma']
    def LemmaID(self):
        return self.properties['lemmaID']
    def Sampa(self):
        return self.properties['sampa']