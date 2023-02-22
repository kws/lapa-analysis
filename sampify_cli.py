from classes.sampify import Sampify
from classes.naf import naf
from os.path import exists, isdir, basename
from pathlib import Path
import argparse, sys, logging, xlwt, os, datetime

def addStreamToLogger(log,file=False,level=logging.DEBUG):
    stream = logging.StreamHandler(sys.stdout)
    if file: stream=logging.FileHandler(file,encoding='utf-8')
    stream.setLevel(level)
    stream.setFormatter(logging.Formatter(u'[%(asctime)s] [%(module)11s] [%(funcName)11s] [%(lineno)3s] [%(levelname)8s] - %(message)s',"%Y-%m-%d %H:%M:%S"))
    log.addHandler(stream)

def save_result(f, counts):
    wb = xlwt.Workbook()
    sh = wb.add_sheet("Sheet1")
    col=1
    sh.write(1, 0, f.split('/')[-1].split('.xls')[0])
    for k in counts.keys():
        sh.write(0, col, k)
        sh.write(1, col, counts[k])
        col+=1
    wb.save(f)

def arg_parser():
    timestamp=str(datetime.datetime.now().strftime("%m-%d-%Y_%H:%M:%S"))

    my_parser = argparse.ArgumentParser(prog='sampify',
                                        usage='%(prog)s --naf [/path/to/naf.xml] --rules [/path/to/rules.xls] --log [/path/to/write/logs] --output [/path/to/write/outputs]',
                                        description='sampfy a naf file')

    my_parser.add_argument('-n', '--naf',         action='store', type=str, required=True, help='the path to the naf file to be translated')
    my_parser.add_argument('-r', '--rules',       action='store', type=str, required=True, help='the path to the rules file')
    my_parser.add_argument('-o', '--output',      action='store', type=str, required=True, help='the path to write the output files')

    args = my_parser.parse_args()

    rules_file = args.rules
    naf_file   = args.naf

    basename_naf=str(basename(naf_file)).split(".")[0]

    out_path   = args.output+"/"+basename_naf+"/"+timestamp
    path = Path(out_path)
    path.mkdir(parents=True)

    if not exists(rules_file):
        print('the rules file does not exist')
        sys.exit()

    if not exists(naf_file):
        print('the naf file does not exist')
        sys.exit()

    return rules_file, naf_file, out_path
    

if __name__ == "__main__":
    rules_file, naf_file, out_path = arg_parser()

    naf_file_name = basename(naf_file)
    out_file = out_path + '/counts.xls'
    trs_file = out_path + '/translations.csv'

    debugLog = logging.getLogger('debugLog')
    debugLog.setLevel(logging.DEBUG)
    #debugLog.setLevel(logging.WARNING)

    addStreamToLogger(debugLog,file=out_path+'/debug.log',level=logging.DEBUG)
    addStreamToLogger(debugLog,file=out_path+'/warn.log', level=logging.WARNING)

    stdoutLog = logging.getLogger('stdoutLog')
    stdoutLog.setLevel(logging.DEBUG)
    addStreamToLogger(stdoutLog,level=logging.DEBUG)

    R=Sampify(rules_file)
    N=naf(naf_file)

    translation_csv=N.translate(R)
    with open(trs_file,"w") as f:
        f.write(translation_csv)
    N.doCount()

    save_result(out_file, N.countSampa.count)