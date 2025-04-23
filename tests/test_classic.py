from lapa_classic.counter import countSampa
from lapa_classic.sampify import Sampify
from lapa_classic.naf import naf
import unittest 
from pathlib import Path

from .conftest import FIXTURES_ROOT

class TestCount(unittest.TestCase):

    def setUp(self):
        self.c = countSampa()
        self.c.add("SEiyEiN")

    def tearDown(self):
        del self.c

    def test_count_single(self):
        self.assertEqual(self.c.count['y'],1, "Incorrect number of 'y' counted")
        self.assertEqual(self.c.count['S'],1, "Incorrect number of 'S' counted")
        self.assertEqual(self.c.count['N'],1, "Incorrect number of 'N' counted")

    def test_count_double(self):
        self.assertEqual(self.c.count['Ei'],2, "Incorrect number of 'Ei' counted")

class compare:
    def __init__(self,ref):
        self.plosives=["p", "b", "t", "d", "k", "g"]
        self.fricatives=["f", "v", "s", "z","x", "G", "h", "z", "S"]
        self.sonorants=["m", "n", "N", "l", "r", "w", "j"]
        self.consonnants=self.plosives+self.fricatives+self.sonorants

        self.checked=["I", "E", "A", "O", "Y", "#"]
        self.monophthongs=["i", "y", "u", "a:"]
        self.potential_diphthongs=["e:", "2:", "o:"]
        self.essential_diphthongs=["Ei", "9y", "Au"]
        self.diphthongs=[]#        "a:i", "o:i", "ui", "iu", "yu", "e:u"
        self.others=["E:", "9:", "O:", "A*", "E*", "O*"]
        self.vowels=self.checked+self.monophthongs+self.potential_diphthongs+self.essential_diphthongs+self.diphthongs+self.others

        self.all=self.consonnants+self.vowels

        self.ref=ref

        self.error=0
        self.total=0

    def add(self,test,list):
        for i in list:
            self.error+=abs(self.ref.count[i]-test.count[i])
            self.total+=self.ref.count[i]

    def get_score(self):
        return self.error, self.total

class TestNaf(unittest.TestCase):
    def setUp(self):
        self.n = naf((FIXTURES_ROOT / "lope001dull01_01.xml"), 0)
        self.a = Sampify((FIXTURES_ROOT / "RULES_A_V1.5.xls").as_posix())
        self.n.translate(self.a)
    def tearDown(self):
        del self.n
    def test_words(self):
        self.assertEqual(self.n.get_wordlist()[0], "Stryt", "Incorrect first word")
        self.assertEqual(self.n.get_wordlist()[-1], "UYT", "Incorrect last word")
    def test_emotion(self):
        self.assertEqual(self.n.WordList[0].EmotionList(), None, "Incorrect first word")
        self.assertEqual(self.n.WordList[70].EmotionList().Emotion()[0].Reference(), 'loyalty', "Incorrect first word")
        self.assertEqual(self.n.WordList[70].EmotionList().Emotion()[1].Reference(), 'sadness', "Incorrect first word")
    def test_sampa(self):
        self.assertEqual(self.n.WordList[0].Sampa(), "strit", "Incorrect first word")
        self.assertEqual(self.n.WordList[-2].Sampa(), "9yt", "Incorrect last word")

if __name__ == "__main__":
    unittest.main(verbosity=2)


