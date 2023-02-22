from classes.sampify import Sampify
import codecs, argparse, sys
from os.path import exists, isdir

def test_dict_quality(ref,dictionary):
    TOT,NOK,result=0,0,''
    with codecs.open(ref, "r", encoding='utf-8') as f:
        for line in f:
            words=line.split()
            if len(words)>1:
                TOT+=1
                NL,REF  =words[0], words[1]
                VERT=dictionary.translate(NL)
                if REF!=VERT:
                    NOK+=1
                    result+="{0:<25}\t{1:<25}\t{2:<25}\n".format(NL,REF,VERT)
    print('error percentage: {0}% ({1} of {2} words)'.format(int(NOK*100/(TOT)),NOK,TOT))
    return result

def arg_parser():
    my_parser = argparse.ArgumentParser(prog='validate',
                                        usage='%(prog)s --rules [/path/to/rules.xls] --test [/path/to/test_file.txt] --output [/path/to/write/outputs]',
                                        description='sampfy a naf file')

    my_parser.add_argument('-r', '--rules', action='store', type=str, required=True, help='the path to the rules file')
    my_parser.add_argument('-t', '--test',  action='store', type=str, required=True, help='the path to the reference file')
    my_parser.add_argument('-o', '--output',action='store', type=str, required=True, help='the path to write the output files')

    args = my_parser.parse_args()

    rules_file = args.rules
    test_file  = args.test
    out_path   = args.output

    if not exists(rules_file):
        print('the rules file does not exist')
        sys.exit()

    if not exists(test_file):
        print('the reference file does not exist')
        sys.exit()

    if not isdir(out_path):
        print('The log path specified does not exist')
        sys.exit()

    return rules_file, test_file, out_path
if __name__ == "__main__":
    RULES, REF, ERRORS = arg_parser()

    with codecs.open(ERRORS,'w', encoding='utf-8') as g:
        g.write(test_dict_quality(REF,Sampify(RULES)))
