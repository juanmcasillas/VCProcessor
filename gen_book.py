
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## --------------------------------------------------------------------------
#
# gen_book.py
# 10/08/2023 (c) Juan M. Casillas <juanm.casillas@gmail.com>
# https://github.com/juanmcasillas/XXXX
#
# Get the files in the input dir, build a PDF book concatenating
# all the files. Created to build the ViaClasica booklet of 
# info, so if you passed the -o switch, only process the official
# files (original info files.)
#
# % python.exe .\gen_book.py -o ".\Croquis\Madrid\Pedriza\Cancho de los Muertos" muertos.pdf
#
# Creates a booklet called muertos.pdf, with only the original ViaClasica files,
# from the input dir.
#
## ---------------------------------------------------------------------------

import fitz
import glob
import os
import sys
import argparse


def process(filelist, fname, vc_files=[]):
    """process the input file filelist and build the pdf booklet

    Args:
        filelist (list): list with the full path to the pdf files
        fname (str): output file name
        vc_files (list, optional): the original viaclasica files. Defaults to [].
    """
    result = fitz.open()
    for pdf in filelist:
        with fitz.open(os.path.join(os.getcwd(), pdf)) as mfile:
            if len(vc_files):
                t = os.path.basename(pdf).lower()
                if not t in vc_files or mfile.page_count > 1:
                    continue

            result.insert_pdf(mfile)
    result.save(fname)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count")
    parser.add_argument("-o", "--only-vc", help="Only via clasica files (no contribs)", action="store_true")
    
    parser.add_argument("input_dir", help="Input dir to process")
    parser.add_argument("output_file", help="output file name")
    args = parser.parse_args()

    file_list = []
    for filename in glob.iglob(args.input_dir + '**/*.pdf', recursive=True):
        file_list.append(filename)

    vc_files = []
    if args.only_vc:
        fd = open("files_pdf_vc.log","r")
        for f in fd.readlines():
            f = f.strip()
            f = os.path.basename(f)
            vc_files.append(f.lower())
        fd.close()

    process(file_list,args.output_file, vc_files=vc_files)

