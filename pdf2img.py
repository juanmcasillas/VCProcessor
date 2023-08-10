# -*- coding: utf-8 -*-
## --------------------------------------------------------------------------
#
# pdf2img.py
# 10/08/2023 (c) Juan M. Casillas <juanm.casillas@gmail.com>
# https://github.com/juanmcasillas/XXXX
#
# Get a directory with PDF files, build a image file with the
# render of the PDF. Useful to build different paper versions
# of the PDF, o add margins later.
#
# % python.exe .\pdf2img.py -t a5 .\Croquis\Alicante\
#
# Creates the image for each PDF found in input directory, and tags the 
# output filename with _a5_ in the middle (useful to find the new generated)
# files. 
#
## ---------------------------------------------------------------------------

from PIL import Image
import glob
import os
import argparse
import fitz


def process(filename, fpath, fext, delete_it=False, cache=True, tag='exp'):
    """get a PDF, render it and save a high res version in PNG

    Args:
        filename (str): the full path to the image file
        fpath (str): the full path, without extension
        fext (str): file's extension (.jpg, .png)
        delete_it (bool, optional): delete the original file after processing. Defaults to False.
        cache (bool, optional): If cache, don't create output the file if previously exists. Defaults to True.
        tag (str, optional): Add the tag value inside the output file name. Defaults to 'exp'.
    """
    output_file = "%s.pdf" % fpath
    if cache and os.path.exists(output_file):
        return

    pdf = fitz.open(filename)
    metadata = pdf.metadata

    index = 0
    for page in pdf:
        img = page.get_pixmap(dpi=300)
        img.save("%s_%s_%02d.png" % (fpath, tag, index))
        index += 1

    if delete_it:
        os.remove(filename)



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count")
    parser.add_argument("-c", "--cache", help="Use the cache, default false", action="store_true")
    parser.add_argument("-d", "--delete", help="Delete the source file (default_false)", action="store_true")
    parser.add_argument("-t", "--tag", help="Add tag into output name (default exp)", action="store", default='exp')

    parser.add_argument("input_dir", help="Input dir to process")
    args = parser.parse_args()

    for filename in glob.iglob(args.input_dir + '**/*.pdf', recursive=True):
        file_name,extension = os.path.splitext(filename)

        print(filename)
        process(filename, file_name, extension, delete_it=args.delete, cache=args.cache, tag=args.tag)



