# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 19:35:27 2017
@author: ruben
"""

import unicodedata
import logging

class Rules:
    def __init__(self, f=None):
        self.debug = logging.getLogger('debugLog')
        self.stdout  = logging.getLogger('stdoutLog')

        self.rules = {'C': {}, 'V': {}, 'P': {}}
        if f != None: self.add_rules(fromfile=f)

    def add_rules(self, fromfile=False, fromline=False):
        if fromline:
            rules = self._read_line_rule()
        if fromfile:
            if fromfile[-4:] == '.csv':
                rules = self._read_csv(fromfile)
            elif fromfile[-5:] == '.json':
                rules = self._read_json(fromfile)
            elif fromfile[-4:] == '.xls':
                self._xlsx_to_csv(fromfile, fromfile[:-5] + "_imported_from_xlsx.csv")
                rules = self._read_csv(fromfile[:-5] + "_imported_from_xlsx.csv")
            elif fromfile[-5:] == '.xlsx':
                self._xlsx_to_csv(fromfile, fromfile[:-5] + "_imported_from_xlsx.csv")
                rules = self._read_csv(fromfile[:-5] + "_imported_from_xlsx.csv")
        if fromfile or fromline:
            self._add_rules(rules)

    def _read_line_rule(self):
        lettyp = str(self.inp('C, V or P? '))
        letter = str(self.inp('first letter? '))
        rultyp = str(self.inp('rules or default? [r/d] '))
        number = int(self.inp('rule number? '))
        descrn = str(self.inp('description? '))
        rulstx = eval(self.inp('rule syntax? '))
        rplced = str(self.inp('letters to be replaced? '))
        rplcby = str(self.inp('replace by? '))
        if lettyp in ['C', 'V', 'P'] and rultyp in ["default", "rules", "r", "d"]:
            if rultyp == 'r':
                rultyp = "rules"
            elif rultyp == 'd':
                rultyp = "default"
            return {lettyp: {letter: {
                rultyp: {number: {"description": descrn, "rule": rulstx, "replaced": rplced, "replaceby": rplcby}}}}}
        else:
            print("wrong input, nothing added")
            return {}

    def inp(self, s):
        return input(s)

    def _add_rules(self, rules):
        self.debug.warning(
            "combining rules can negatively affect the order of rules. Always check the combination of rules manually")
        for i in rules.keys():
            for j in rules[i].keys():
                if j not in self.rules[i].keys():  # case where a letter was not in the rule set yet
                    self.rules[i][j] = {'default': {}, 'rules': {}}
                    if 'default' in rules[i][j].keys():
                        for k in rules[i][j]['default'].keys():
                            self.debug.debug("checking rule {0}:{1}:default:{2} before adding".format(i, j, k))
                            self._check_rule_syntax(rules[i][j]['default'][k])
                        self.rules[i][j]['default'] = rules[i][j]['default']
                        self.debug.debug("all {0}:{1}:default rules added".format(i, j))
                    else:
                        self.debug.warning("{0}:{1} might not have a default".format(i, j))
                    if 'rules' in rules[i][j].keys():
                        for k in rules[i][j]['rules'].keys():
                            self.debug.debug("checking rule {0}:{1}:rules:{2} before adding".format(i, j, k))
                            self._check_rule_syntax(rules[i][j]['rules'][k])
                        self.rules[i][j]['rules'] = rules[i][j]['rules']
                        self.debug.debug("all {0}:{1}:rules rules added".format(i, j))
                else:
                    if 'default' in rules[i][j].keys() and len(self.rules[i][j]['default'].keys()) > 0:
                        self.debug.warning(
                            "default rule already present for {0}:{1}, while trying to add one. There might be multiple defaults now".format(
                                i, j))
                    for k in rules[i][j].keys():
                        for l in rules[i][j][k].keys():
                            if l not in self.rules[i][j][k].keys():
                                self.debug.debug("checking rule {0}:{1}:{2}:{3} before adding".format(i, j, k, l))
                                self._check_rule_syntax(rules[i][j][k][l])
                                self.rules[i][j][k][l] = rules[i][j][k][l]
                                self.debug.debug("rule {3} added to {0}:{1}:{2}".format(i, j, k, l))
                            else:
                                self.debug.warning(
                                    "attempting to overwrite a rule, new rule was ignored. (rule {0}:{1}:{2}:{3})".format(
                                        i, j, k, l))

    def _check_rule_syntax(self, l):
        if type(l["rule"]) == int:
            if l["rule"] < 1:
                self.debug.warning("A rule has a too small required number of syllables: {0}".format(l["rule"]))
            elif l["rule"] > 10:
                self.debug.warning("A rule has a very high required number of syllables: {0}".format(l["rule"]))
        elif type(l["rule"]) == list:
            for m in l["rule"]:
                if type(m) == int:
                    if m not in [0, 1]:
                        self.debug.warning(
                            "the syntax within a rule is badly formed, presence/absence of a character should be expressed with 1/0: {0}".format(
                                l["rule"]))
                else:
                    if len(m) not in [1, 3]:
                        self.debug.warning(
                            "the syntax within a rule is badly formed, it should be expressed in 1 or 3 characters: {0}".format(
                                l["rule"]))
                    if len(m) == 3 and m[1] != '=':
                        self.debug.warning(
                            "the syntax within a rule is badly formed, it should be united by an = sign: {0}".format(
                                l["rule"]))
                    if len(m) == 3 and m[0] not in ["V", "C"]:
                        self.debug.warning(
                            "the syntax within a rule is badly formed, the left side of the equation should be C or V: {0}".format(
                                l["rule"]))

    def _read_json(self, f):
        import json
        with open(f) as data_file:
            self.debug.debug("json rule file {0} successfully parsed".format(f))
            return json.load(data_file)

    def _write_json(self, f):
        import json
        with open(f, 'w') as outfile:
            json.dump(self.rules, outfile, indent=4, sort_keys=True, separators=(',', ':'))
            self.debug.debug("json rule file {0} successfully written".format(f))

    def _read_csv(self, f):
        with open(f) as data_file:
            content = [x.strip() for x in data_file.readlines()]
            rules, headers = {}, content[0].split(';')
            for i in content[1:]:
                elements = i.split(';')
                if elements[0] not in rules.keys():
                    rules[elements[0]] = {}
                if elements[1] not in rules[elements[0]].keys():
                    rules[elements[0]][
                        elements[1]] = {}
                if elements[2] not in rules[elements[0]][elements[1]].keys():
                    rules[elements[0]][elements[1]][elements[2]] = {}
                if int(elements[3].split('.')[0]) not in rules[elements[0]][elements[1]][elements[2]].keys():
                    rules[elements[0]][elements[1]][elements[2]][int(elements[3].split('.')[0])] = {
                        headers[4]: elements[4], headers[5]: eval(elements[5]),
                        headers[6]: elements[6], headers[7]: elements[7]}
        self.debug.debug("csv rule file {0} successfully parsed".format(f))
        return rules

    def _xlsx_to_csv(self, f, g):
        import xlrd, csv
        wb = xlrd.open_workbook(f)
        sh = wb.sheet_by_name('RULES')
        your_csv_file = open(g, 'w')
        wr = csv.writer(your_csv_file, quoting=csv.QUOTE_MINIMAL, delimiter=';')
        for rownum in range(sh.nrows):
            wr.writerow(sh.row_values(rownum))
        your_csv_file.close()

class Sampify(Rules):
    def _test_case(self, tvl, tvt, r):
        if type(r) is int:
            if r == 1:
                if tvl != None: return True
            elif r == 0:
                if tvl == None: return True
        elif len(r) == 1:
            if r in ['C', 'V']:
                if r == tvt: return True
            else:
                if r == tvl: return True
        elif len(r) == 3:
            if r[0] in ['C', 'V']:
                if r[2] == '1':
                    if r[0] == tvt: return True
                elif r[2] == '0':
                    if r[0] != tvt: return True
                else:
                    if r[2] == tvl: return True
        return False

    def _test_rule(self, wl, tl, Nsyllab, rule, position, rulenumber):
        all_outcomes = []
        if type(rule['rule']) is int:
            if rule['rule'] == Nsyllab:
                return True
            else:
                return False
        for i in range(len(rule['rule'])):
            if len(wl[position:]) < i + 1:
                all_outcomes.append(self._test_case(None, None, rule['rule'][i]))
            else:
                all_outcomes.append(self._test_case(wl[position:][i], tl[position:][i], rule['rule'][i]))
        if False not in all_outcomes:
            self.debug.debug("rule {0} is matching".format(rulenumber))
            return True
        self.debug.debug("rule {0} is not matching".format(rulenumber))
        return False

    def _find_rule(self, wl, tl, Nsyllab, position, rules):
        if position == 0 and wl[0] in rules['P'].keys():
            for i in sorted(rules['P'][wl[position]]['default'].keys()):
                self.debug.debug("testing prefix rule {0}:{1}:{2}".format('P', wl[position], i))
                if self._test_rule(wl, tl, Nsyllab, rules['P'][wl[position]]['default'][i], position, i):
                    return i, rules['P'][wl[position]]['default'][i]
        for i in sorted(rules[tl[position]][wl[position]]['rules'].keys()):
            self.debug.debug("testing rule {0}:{1}:{2}".format(tl[position], wl[position], i))
            if self._test_rule(wl, tl, Nsyllab, rules[tl[position]][wl[position]]['rules'][i], position, i):
                return i,rules[tl[position]][wl[position]]['rules'][i]
        self.debug.debug("no rule found, default rule is used: {0}:{1}:{2}".format(tl[position],wl[position],0))
        return 0, rules[tl[position]][wl[position]]['default'][0]

    def _apply_rule(self, log, sampa, position, rule, rulenum):
        srce, dest = list(rule['replaced']), list(rule['replaceby'])
        lensrce, lendest = len(srce), len(dest)
        olog = log[:position] + ['S'] * lendest + log[position + lensrce:]
        osampa = sampa[:position] + dest + sampa[position + lensrce:]
        self.debug.debug(
            "rule {0} applied to sampa '{1}' on position {2}. Output: '{3}'".format(rulenum, "".join(sampa), position,
                                                                                    "".join(osampa)))
        return olog, osampa

    def _find_apply(self, log, word, syllables, rules):
        for i in range(len(log)):
            if log[i] != 'S':
                self.debug.debug("Searching applicable rule for position {0} of '{1}'".format(i, "".join(word)))
                applicable_rule_n, applicable_rule = self._find_rule(word, log, syllables, i, rules)
                log, word = self._apply_rule(log, word, i, applicable_rule, applicable_rule_n)
                return log, word

    def _num_syll(self, l):
        if l[0] == 'C':
            vow, lettergrepen = False, 0
        else:
            vow, lettergrepen = True, 1
        for i in range(1, len(l)):
            if l[i] == 'C' and vow == True:  vow = False
            if l[i] == 'V' and vow == False: vow, lettergrepen = True, lettergrepen + 1
        self.debug.debug("Counting syllables in word, found {0}".format(lettergrepen))
        return lettergrepen

    def _gen_chlog(self, word):
        word_l, chlog = list(word), []
        for i in word_l:
            if i in self.rules['V'].keys():
                chlog.append('V')
            elif i in self.rules['C'].keys():
                chlog.append('C')
            else:
                chlog.append('S')
                self.debug.warning("Unknown letter in word {1}: '{0}'. Letter will not be translated.".format(i,word))
        return word_l, chlog

    def clean(self, w):
        # TO DO: remove punctuation
        self.debug.debug("removing accents")
        w_noacc=self.strip_accents(w.lower())
        return w_noacc
        #for p in self.settings["punctuation"]:
        #    self.CleanWord = self.CleanWord.replace(p, '')

    def strip_accents(self,s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
                       if unicodedata.category(c) != 'Mn')

    def translate(self, word):
        self.debug.debug("starting sampyfication of word '{0}'".format(word))
        word_clean=self.clean(word)
        word_l, chlog = self._gen_chlog(word_clean)
        syllables = self._num_syll(chlog)
        while 'V' in chlog or 'C' in chlog: chlog, word_l = self._find_apply(chlog, word_l, syllables, self.rules)
        self.debug.debug("word '{0}' successfully sampified: '{1}'".format(word, "".join(word_l)))
        return "".join(word_l)


# standaard woordenlijst
# suffix als 1e doen?
