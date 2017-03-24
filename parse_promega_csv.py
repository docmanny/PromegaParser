#!/usr/bin/env python3
""" Simple script to parse through the Promega GloMax Multi+ file and extract read CSVs. Tested on both ApoTox Glo and
Dual Luciferase outputs."""
from pathlib import Path
import argparse
__version__ = "1.1"
__author__ = "Juan Manuel Vazquez"


parser = argparse.ArgumentParser(description='A simple script to parse through the Promega GloMax Multi+ CSV file '
                                             'and extract the tables of read values as CSVs. \nTested on both Dual '
                                             'Luciferase and ApoTox Glo outputs.\n'
                                             '\n In a nutshell, the script will parse through the file line-by-line; '
                                             'when it finds description text about the protocol, it saves it to a file '
                                             'called "Protocol_Description.txt, and when it finds read data from a '
                                             'plate it saves the plate results as a CSV file that will be titled with '
                                             'the original plate title. Finally, the script will return a list of '
                                             'filenames made.'
                                             '\n Note that if you run this on some other GloMax output, I would '
                                             'strongly recommend that you turn on verbose output to see how its dealing'
                                             'with possibly unknown lines.'
                                             '\n[Script version: {}]'.format(__version__))

parser.add_argument('fileloc', help="Location of the Promega GloMax CSV output to be split into tables.")
parser.add_argument("-v", "--verbose", action='store_true', default=False, help="Activate Verbose Output")
parser.add_argument('--version', action='version', version=__version__)
args = parser.parse_args()

promega_file = Path(args.fileloc)
dir_root = Path(str(promega_file.parent), str(promega_file.stem).replace(' ', '_'))
try:
    if args.verbose:
        print('Creating directory: ', str(dir_root.absolute()), end='... ')
    dir_root.mkdir(parents=True)
    if args.verbose:
        print('Success!')
except FileExistsError:
    if args.verbose:
        print('Directory already exists! ')
    pass

if promega_file.exists():
    if args.verbose:
        print('Found file: ', str(promega_file.absolute()))
else:
    raise FileNotFoundError(str(promega_file.absolute()))

if args.verbose:
    print('Opening and reading file... ')
count = 0
filename_list = list()
with promega_file.open() as f_in:
    for line in f_in.readlines():
        if line.startswith('Protocol'):
            prot_filename = str(dir_root.absolute()) + '/' + 'Protocol_Description.txt'

            if args.verbose:
                print('Found Protocol Description! Writing to file: ', prot_filename)
            if Path(prot_filename).exists() and Path(prot_filename).is_file():
                count += 1
                if args.verbose:
                    print('{0}already exists! Appending a _{1} to end of new file!'.format(f_filename, count))
                prot_filename = str(dir_root.absolute()) + '/' + 'Protocol_Description.txt'.format(count)
            f_out = Path(prot_filename).open('w')
            f_out.write(line)
            filename_list.append(prot_filename)

        elif line.startswith(',Read'):
            f_filename = str(dir_root.absolute()) + '/' + line.lstrip(',').strip('\n').replace(' ', '_') + '.csv'
            if args.verbose:
                print('Found a read file! Writing to file: ', f_filename)
            if Path(f_filename).exists() and Path(f_filename).is_file():
                count += 1
                if args.verbose:
                    print('{0}already exists! Appending a _{1} to end of new file!'.format(f_filename, count))
                f_out = Path(f_filename + '_{}'.format(count)).open('w')
            else:
                f_out = Path(f_filename).open('w')
            filename_list.append(f_filename)

        elif line.startswith('Results'):
            f_filename = str(dir_root.absolute()) + '/' + line.lstrip(',').strip('\n').replace(' ', '_') + '.csv'
            if args.verbose:
                print('Found a Results File! Writing to file: ', f_filename)
            f_out = Path(f_filename).open('w')
            filename_list.append(f_filename)

        elif line.startswith('Step') or line.startswith('Notes'):
            if args.verbose:
                print('Found protocol info! Adding to file: ', prot_filename)
            with Path(prot_filename).open('w+') as f_out:
                f_out.write(line)

        elif line == '\n':
            if not f_out.closed:
                if args.verbose:
                    print('\tReached newline character, closing output file!')
                f_out.close()
            else:
                if args.verbose:
                    print('Reached newline character, and no outfile is open, continuing...')

        elif line.startswith(','):
            if args.verbose:
                print('\tFound line starting with comma! Stripping first comma so that reading it later doesn\'t lead '
                      'to a blank column...')
            if line.startswith(',,'):
                f_out.write(line.replace(',,', ','))
            elif ',,' in line and not line.startswith(',,'):
                f_out.write(line)
            else:
                f_out.write(line.lstrip(',').replace(':', ','))

        else:
            if args.verbose:
                print('** Skipping this line, not saving it:', line.strip('\n'), end=' **\n')
    if args.verbose:
        print('Finished!')

