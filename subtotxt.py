# SRT or WEBVTT to plain Text
# Author: NebularNerd Version 2.1 (July 2024)
# https://github.com/NebularNerd/subtotxt
# Import required packages
import sys
import os
import argparse
import pkg_resources
import subprocess
import re
from pathlib import Path

# Install send2trash and charset_normalizer if missing.
# See https://pypi.org/project/Send2Trash/
# See https://github.com/Ousret/charset_normalizer
REQUIRED = {
  'send2trash','charset-normalizer'
}

installed = {pkg.key for pkg in pkg_resources.working_set}
missing = REQUIRED - installed

if missing:
    print('Installing missing modules, please wait a few moments. This only happens once.')
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL) 
    print('Done, thanks for waiting')

from send2trash import send2trash
from charset_normalizer import from_path

# Clear screen win/*nix friendly
def cls():
    os.system('cls' if os.name=='nt' else 'clear')
cls()

# Setup argparse
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description='Quickly strip SRT or WEBVTT of subtitle numbers and timestamp, then save to plain text file \nVisit https://github.com/NebularNerd/subtotxt for more information')                                               
parser.add_argument("--file", "-f", type=str, required=True, help='Path to .srt or .vtt file, enclose in quotes if path has spaces')
parser.add_argument("--utf8", "-8", default=False, action="store_true", required=False, help='Force output file to use UTF-8 instead of input encoding')
parser.add_argument("--pause", "-p", default=False, action="store_true", required=False, help='Pauses at sanity check info to allow viewing before continuing')
parser.add_argument("--screen", "-s", default=False, action="store_true", required=False, help='Prints the conversion to the console as well as the file')
parser.add_argument("--copy", "-c", default=False, action="store_true", required=False, help='Copies input to output without change, appends -copy to filename')
parser.add_argument("--overwrite", "-o", default=False, action="store_true", required=False, help='Skips asking for permission to overwrite, will auto-delete old file and create a new one')
parser.add_argument("--oneliners", "-1", default=False, action="store_true", required=False, help='Write all sentences in one line, even if the original divides it into many lines or subtitles.')
args = parser.parse_args()

# Setup file wrangling stuff and sanity checks
ifile = Path(args.file)
ofile = ifile.with_suffix('.txt')
cfile = ifile.with_stem(f"{ifile.stem}-copy")
result = from_path(ifile).best() # charset_normalizer guess encoding
encoding = result.encoding
if result is not None and encoding == "utf_8" and result.bom:
    encoding += "_sig" # adds sig for utf_8_sig/bom files
if result is not None and encoding == "utf_16" and result.bom:
        encoding += "_sig" # adds sig for utf_16_sig/bom files        
confidence = 1.0 - result.chaos # gives probability of match being correct

#Do stuff
print('SUB to TXT 2.0\n')
print('Input file  : \n',ifile)
if args.copy:
    print('Output file : \n',cfile,'\n')
    deleteme = cfile
else:
    print('Output file : \n',ofile,'\n')
    deleteme = ofile
    print('Detected Character Encoding:',encoding)
    print('Confidence of encoding     : {:0.2f}%'.format(confidence*100))
if args.utf8:
    print('Output encoding forced to UTF-8')
    encset="utf8"
else:
    print('Output will use input encoding')
    encset=encoding
print('\n\n')
answer = None
if args.pause:
    while answer not in ("y","n"): 
        answer = input("Ready to start? [y/n]")
        if answer == "y": 
            print('Starting...')
        elif answer == "n": 
            print ("OK, bye for now...\n\n")
            sys.exit()
        else: 
            print("Please enter y or n.") 

# Check for old file
answer = None
if not args.overwrite:
    if deleteme.is_file():
        while answer not in ("y","n"): 
            answer = input("Output file already exists, delete and make a new one? [y/n]")       
            if answer == "y": 
                send2trash(deleteme)
            elif answer == "n": 
                print ("OK, bye for now...\n\n")
                sys.exit()
            else: 
                print("Please enter y or n.") 

# Test File Format (in case of extension error) and set flags
webvtt = 0
srt = 0
if not args.copy:
    with open(ifile, 'r', encoding=encoding) as testsub:
        for line in testsub:
            if "WEBVTT" in line:
                webvtt = 1
            elif line.strip('\n') == "1" and re.search("(.*:.*:.*-->.*:.*:.*)",next(testsub)):
                srt = 1
            
# SRT format
if srt == 1:
    with open(ifile, 'r', encoding=encoding) as original, open(ofile, 'w', encoding=encset) as new:
        subnum = 1
        subnumstr = str(subnum)
        for line in original:
            if line.strip('\n') == subnumstr and re.search("(.*:.*:.*-->.*:.*:.*)",next(original)): 
                subnum = subnum+1
                subnumstr = str(subnum)
                #Ignore SRT Subtitle # and Timecode lines
            elif not line.strip('\n') == '':
                if args.screen: print(line, end='')
                if args.oneliners:
                    line = line.strip()
                    if line[-1] in [".", "?", "!", "…"]:
                        new.write(line + '\n')
                    else:
                        new.write(line + ' ')
                else:
                    new.write(line)

# WEBVTT format
if webvtt == 1:
    with open(ifile, 'r', encoding=encoding) as original, open(ofile, 'w', encoding=encset) as new:
        subnum = 1
        subnumstr = str(subnum)
        for line in original:
            if "WEBVTT" in line or re.search("^Kind:.*$",line) or re.search("^Language:.*$",line) or re.search("(.*:.*:.*-->.*:.*:.*)",line):
                line = ''
            if not line.strip('\n') == '':
                if args.screen: print(line, end='')
                if args.oneliners:
                    line = line.strip()
                    if line[-1] in [".", "?", "!", "…"]:
                        new.write(line + '\n')
                    else:
                        new.write(line + ' ')
                else:
                    new.write(line)

# Copy mode
if args.copy:
    with open(ifile, 'r', encoding=encoding) as original, open(cfile, 'w', encoding=encset) as new:
        for line in original:
            if args.screen: print(line, end='')
            new.write(line)   
    
print('\nFinished\n')
















