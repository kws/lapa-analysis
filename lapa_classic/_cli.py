import click
import logging
import sys
import xlwt
import datetime
from pathlib import Path
from os.path import exists, isdir, basename
from .sampify import Sampify
from .naf import naf

def setup_logging(out_path):
    """Setup logging configuration"""
    debug_log = logging.getLogger('debugLog')
    debug_log.setLevel(logging.DEBUG)
    
    # Debug log file
    debug_handler = logging.FileHandler(f'{out_path}/debug.log', encoding='utf-8')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] [%(module)11s] [%(funcName)11s] [%(lineno)3s] [%(levelname)8s] - %(message)s',
        "%Y-%m-%d %H:%M:%S"
    ))
    debug_log.addHandler(debug_handler)
    
    # Warning log file
    warn_handler = logging.FileHandler(f'{out_path}/warn.log', encoding='utf-8')
    warn_handler.setLevel(logging.WARNING)
    warn_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] [%(module)11s] [%(funcName)11s] [%(lineno)3s] [%(levelname)8s] - %(message)s',
        "%Y-%m-%d %H:%M:%S"
    ))
    debug_log.addHandler(warn_handler)
    
    # Console output
    stdout_log = logging.getLogger('stdoutLog')
    stdout_log.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    stdout_log.addHandler(console_handler)

def save_result(f, counts):
    """Save results to Excel file"""
    wb = xlwt.Workbook()
    sh = wb.add_sheet("Sheet1")
    col = 1
    sh.write(1, 0, f.split('/')[-1].split('.xls')[0])
    for k in counts.keys():
        sh.write(0, col, k)
        sh.write(1, col, counts[k])
        col += 1
    wb.save(f)

def test_dict_quality(ref, dictionary):
    """Test dictionary quality against reference file"""
    TOT, NOK, result = 0, 0, ''
    with open(ref, "r", encoding='utf-8') as f:
        for line in f:
            words = line.split()
            if len(words) > 1:
                TOT += 1
                NL, REF = words[0], words[1]
                VERT = dictionary.translate(NL)
                if REF != VERT:
                    NOK += 1
                    result += f"{NL:<25}\t{REF:<25}\t{VERT:<25}\n"
    click.echo(f'error percentage: {int(NOK*100/(TOT))}% ({NOK} of {TOT} words)')
    return result

@click.group()
def cli():
    """LAPA CLI tools for processing and validating NAF files"""
    pass

@cli.command()
@click.option('--naf', '-n', required=True, type=click.Path(exists=True), help='Path to the NAF file to be translated')
@click.option('--rules', '-r', required=True, type=click.Path(exists=True), help='Path to the rules file')
@click.option('--output', '-o', required=True, type=click.Path(), help='Path to write the output files')
def sampify(naf, rules, output):
    """Process a NAF file using the specified rules"""
    timestamp = datetime.datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    basename_naf = basename(naf).split(".")[0]
    out_path = f"{output}/{basename_naf}/{timestamp}"
    
    # Create output directory
    Path(out_path).mkdir(parents=True, exist_ok=True)
    
    # Setup logging
    setup_logging(out_path)
    
    # Process files
    out_file = f'{out_path}/counts.xls'
    trs_file = f'{out_path}/translations.csv'
    
    R = Sampify(rules)
    N = naf(naf)
    
    translation_csv = N.translate(R)
    with open(trs_file, "w", encoding='utf-8') as f:
        f.write(translation_csv)
    
    N.doCount()
    save_result(out_file, N.countSampa.count)
    
    click.echo(f"Processing complete. Results saved to {out_path}")

@cli.command()
@click.option('--rules', '-r', required=True, type=click.Path(exists=True), help='Path to the rules file')
@click.option('--test', '-t', required=True, type=click.Path(exists=True), help='Path to the reference file')
@click.option('--output', '-o', required=True, type=click.Path(), help='Path to write the output files')
def validate(rules, test, output):
    """Validate rules against a reference file"""
    if not isdir(output):
        click.echo('The output path specified does not exist')
        sys.exit(1)
    
    errors_file = f"{output}/validation_errors.txt"
    with open(errors_file, 'w', encoding='utf-8') as g:
        g.write(test_dict_quality(test, Sampify(rules)))
    
    click.echo(f"Validation complete. Results saved to {errors_file}")

if __name__ == '__main__':
    cli() 