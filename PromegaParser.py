#!/usr/bin/env python3

import click
from pathlib import Path

__version__ = "2.0"

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('file_locations', type=click.Path(exists=True), nargs=-1)
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode')
@click.option('--output_directory', type=click.Path(), default="./",
              help='Name of output directory for split files')
@click.version_option(version=__version__)
def main(file_locations, output_directory, verbose):
    """
    A simple script to parse through the Promega GloMax Multi+ CSV file and extract
    the tables of read values as CSVs. Tested on both Dual Luciferase and
    ApoTox Glo outputs. Accepts a list of file paths as input.
    Note that if you run this on some other GloMax output, I would
    strongly recommend that you turn on verbose output to see how its dealing
    with possibly unknown lines.
    """

    output_directory = Path(output_directory)

    try:
        if verbose:
            print('Creating directory: {}...'.format(str(output_directory.absolute())))
        output_directory.mkdir(parents=True)
        if verbose:
            print('Success!')
    except FileExistsError:
        if verbose:
            print('Directory already exists! ')
    for floc in [Path(i) for i in file_locations]:
        outdir = output_directory / floc.stem.replace(' ', '_')
        try:
            if verbose:
                print('Creating directory: {}...'.format(str(floc)))
            outdir.mkdir(parents=True)
            if verbose:
                print('Success!')
        except FileExistsError:
            if verbose:
                print('Directory already exists!')
        if verbose:
            print('Opening and reading file... ')
        count = 0
        filename_list = list()
        with floc.open() as f_in:
            for line in f_in.readlines():
                if line.startswith('Protocol'):
                    prot_filename = outdir / 'Protocol_Description.txt'
                    if verbose:
                        print('Found Protocol Description! Writing to file {}'.format(str(prot_filename)))
                    prot_filename.touch()
                    f_out = prot_filename.open('w+')
                    f_out.write(line)
                    filename_list.append(prot_filename)
                elif line.startswith("Step"):
                    tmpname = line.replace('.', ',').replace(" ", "").split(",")[0:3]
                    f_filename = outdir / "_".join(tmpname)
                elif line.startswith(',Read'):
                    f_filename = f_filename.with_name(f_filename.name + "_" +
                                                      line.lstrip(',').strip('\n').replace(' ', '_') +
                                                      '.csv')
                    if verbose:
                        print('Found a read file! Writing to file: ', f_filename)
                    if Path(f_filename).exists() and Path(f_filename).is_file():
                        count += 1
                        if verbose:
                            print('{0} already exists! Appending a _{1} to end of new file!'.format(f_filename, count))
                        f_out = f_filename.with_name(f_filename.stem +
                                                     '_{}'.format(count) +
                                                     f_filename.suffix).open('w')
                    else:
                        f_out = Path(f_filename).open('w')
                    filename_list.append(f_filename)
        
                elif line.startswith('Results'):
                    f_filename = outdir / "".join([line.lstrip(',').strip('\n').replace(' ', '_'), '.csv'])
                    if verbose:
                        print('Found a Results File! Writing to file: ', f_filename)
                    f_out = Path(f_filename).open('w')
                    filename_list.append(f_filename)
        
                elif line.startswith('Notes'):
                    if verbose:
                        print('Found protocol info! Adding to file: ', prot_filename)
                    with prot_filename.open('w+') as f_out:
                        f_out.write(line)
        
                elif line == '\n':
                    if not f_out.closed:
                        if verbose:
                            print('\tReached newline character, closing output file!')
                        f_out.close()
                    else:
                        if verbose:
                            print('Reached newline character, and no outfile is open, continuing...')
        
                elif line.startswith(','):
                    if verbose:
                        print('\tFound line starting with comma! Stripping first comma so that reading it later doesn\'t lead '
                              'to a blank column...')
                    if line.startswith(',,'):
                        f_out.write(line.replace(',,', ','))
                    elif ',,' in line and not line.startswith(',,'):
                        f_out.write(line)
                    else:
                        f_out.write(line.lstrip(',').replace(':', ','))
                elif line.startswith("PlateResults"):
                    continue
                else:
                    if verbose:
                        print('** Skipping this line, not saving it:', line.strip('\n'), end=' **\n')
            if verbose:
                print('Finished!')


if __name__=='__main__':
    main()