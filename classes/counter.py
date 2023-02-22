# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 19:35:27 2017
@author: ruben
"""
import logging
class countSampa:
    sampa_double = ["a:", "e:", "2:", "o:", "Ei", "9y", "Au", "E:", "9:", "O:", "A*", "E*", "O*"]
    sampa_single = ["I", "E", "A", "O", "Y", "#", "i", "y", "u", "p", "b", "t", "d", "k", "g", "f", "v", "s", "z",
                         "x", "G", "h", "z", "S", "m", "n", "N", "l", "r", "w", "j"]

    def __init__(self,double=sampa_double, single=sampa_single):
        self.debug = logging.getLogger('debugLog')
        self.stdout  = logging.getLogger('stdoutLog')

        self.sampa=double+single
        self.count=dict.fromkeys(self.sampa,0)

    def sampaCount(self):
        return self.count

    def add(self,w):
        self.debug.info("adding {0} to counter".format(w))
        wordlist=list(w)
        while len(wordlist)>0:
            if len(wordlist)>1 and wordlist[0]+wordlist[1] in self.sampa_double:
                self.count[wordlist[0]+wordlist[1]]=self.count[wordlist[0]+wordlist[1]]+1
                self.debug.info("found {0}, adding 1 to total count (was {1})".format(wordlist[0]+wordlist[1], self.count[wordlist[0]+wordlist[1]]-1))
                wordlist=wordlist[2:]
            elif wordlist[0] in self.sampa_single:
                self.count[wordlist[0]]=self.count[wordlist[0]]+1
                self.debug.info("found {0}, adding 1 to total count (was {1})".format(wordlist[0], self.count[wordlist[0]]-1))
                wordlist=wordlist[1:]
            else:
                self.debug.warning("no corresponding SAMPA found for {0}, removing letter".format(wordlist[0]))
                wordlist = wordlist[1:]

class countEmotions:
    def __init__(self):
        self.debug = logging.getLogger('debugLog')
        self.stdout  = logging.getLogger('stdoutLog')

        self.emotions=['love', 'joy', 'desire', 'hope', 'compassion', 'happiness', 'honor', 'loyalty', 'wonder', 'moved', 'aquiescence', 'benevolence', 'pride', 'dedication', 'trust', 'awe', 'relief', 'sadness', 'fear', 'anger', 'despair', 'vindictiveness', 'hatred', 'remorse', 'worry', 'shame', 'heavyHeartedness', 'disgust', 'spitefulness', 'annoyance', 'envy', 'suspicion', 'offended', 'unhappiness', 'dissapointment', 'greed', 'loss', 'other','unknown']
        self.clusters=['sadness', 'love', 'anger', 'fear', 'joy', 'desire', 'despair', 'disgust', 'posSentiments', 'compassion', 'prideHonour', 'other','unknown']
        self.count={
            'emotions':dict.fromkeys(self.emotions, 0),
            'clusters':dict.fromkeys(self.clusters, 0)
        }

    def addEmotion(self,e):
        if e in self.count['emotions']:
            self.count['emotions'][e]+=1
            self.debug.info('added 1 to count of emotion {0} (was {1})'.format(e,self.count['emotions'][e]-1))
        else:
            self.count['emotions']['unknown'] += 1
            self.debug.info('unknown emotion, count added to unknown')
    def addCluster(self,c):
        if c in self.count['clusters']:
            self.count['clusters'][c]+=1
            self.debug.info('added 1 to count of cluster {0} (was {1})'.format(c,self.count['clusters'][c]-1))
        else:
            self.count['clusters']['unknown'] += 1
            self.debug.info('unknown cluster, count added to unknown')
    def emotionCount(self):
        return self.count['emotions']
    def clusterCount(self):
        return self.count['clusters']
        