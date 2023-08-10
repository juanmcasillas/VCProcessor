#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## --------------------------------------------------------------------------
#
# img2pdf.py
# 10/08/2023 (c) Juan M. Casillas <juanm.casillas@gmail.com>
# https://github.com/juanmcasillas/XXXX
#
# Get a directory with image files, build a PDF with the paper
# size selected, at the required DPI. Useful to build booklets
# of previously extracted images (from PDF) or a list of images.
#
# % python.exe .\img2pdf.py -mx 7 -my 7 .\Croquis\Alicante\ -p A5
#
# Creates the pdf for each files in the input directory, with a margin 
# of 7mm in all sides, on a A5 page.
#
## ---------------------------------------------------------------------------

from PIL import Image
import glob
import os
import sys
import argparse

# in mm, as portrait (width, height)

PAPER_SIZES= {
    'A0':  (841, 1189),
    'A1':  (594, 841 ),
    'A2':  (420, 594 ),
    'A3':  (297, 420 ),
    'A4':  (210, 297 ),
    'A5':  (148, 210 ),
    'A6':  (105, 148 ),
    'A7':  (74 , 105 ),
    'A8':  (52 , 74  ),
    'A9':  (37 , 52  ),
    'A10': (26 , 37  ),
    'Letter':    (216,   279  ),
    'Legal':     (215.9, 355.6),
    'Executive': (184.2, 266.7),
    'Tabloid':   (279,   432  )
}

def process(filename, fpath, fext, delete_it=False, margin=(0,0), cache=True, paper='A4'):
    """generate the PDF file from an image file

    Args:
        filename (str): the full path to the image file
        fpath (str): the full path, without extension
        fext (str): file's extension (.jpg, .png)
        delete_it (bool, optional): delete the original file after processing. Defaults to False.
        margin (tuple, optional): X and Y margin, in mm. Defaults to (0,0).
        cache (bool, optional): If cache, don't create output the file if previously exists. Defaults to True.
        paper (str, optional): Size of the PDF paper. Defaults to 'A4'.
    """


    PAPER_WIDTH, PAPER_HEIGHT = PAPER_SIZES[paper]
    DEFAULT_DPI = 96

    output_file = "%s.pdf" % fpath
    if cache and os.path.exists(output_file):
        return

    img = Image.open(filename)
    w,h = img.size
    x_dpi, y_dpi = img.info['dpi'] if 'dpi' in img.info else (DEFAULT_DPI,DEFAULT_DPI)
    mode = 'L' if w > h else 'P'
    
    paper_size = ( 
            int(PAPER_WIDTH  * x_dpi / 25.4), 
            int(PAPER_HEIGHT * y_dpi / 25.4) 
            )
    tgt_size = paper_size if mode == 'P' else tuple(reversed(paper_size))
    
    margin = ( int(2*margin[0]*x_dpi / 25.4), 
               int(2*margin[1]*y_dpi / 25.4) )

    tgt_size = ( tgt_size[0] - margin[0] , tgt_size[1] - margin[1] )
   
    
    ratio_h = float(tgt_size[0]) / tgt_size[1] 
    ratio_v = float(tgt_size[1]) / tgt_size[0] 
    
    # scale to max size, if portrait, maximize the height, if landscape, maximize width

    if mode == 'P':
        sc_h = tgt_size[1]
        sc_w = sc_h * ratio_v # v
        if sc_w > tgt_size[0]:
            sc_w = tgt_size[0]
            sc_h = sc_w *  ratio_v # v
            if sc_h > tgt_size[1]: 
                r2 = float(tgt_size[1]) / tgt_size[0]
                sc_w = sc_h * r2                
                #print("ops H")
    else:
        # w < h
        sc_w = tgt_size[0]
        sc_h = sc_w * ratio_h # h
        if sc_h > tgt_size[1]:  # overflow in the height, must calculate available size.
            sc_h = tgt_size[1]
            sc_w = sc_h * ratio_h # h
            if sc_w > tgt_size[0]:
                r2 = float(tgt_size[0]) / tgt_size[1]
                sc_w = sc_h * r2
                #print("ops W")

    sc_w, sc_h = tuple(map(lambda x: int(x), (sc_w, sc_h)))
    resized_img = img.resize( (sc_w, sc_h), Image.LANCZOS )

    print("Paper: %s; scaling from (%d,%d) -> (%d,%d)  target_res: %d,%d // (dpi: %d,%d, mode: %s, ratio: %3.3f, %3.3f, margin: %d,%d)" % (
        paper,
        w,h,tgt_size[0],tgt_size[1], 
        sc_w, sc_h, 
        x_dpi,y_dpi, mode, ratio_h, ratio_v, margin[0], margin[1]))

    paperim = Image.new('RGB',
                    paper_size if mode=='P' else tuple(reversed(paper_size)),   
                    (255, 255, 255))  # White
    
    x = (paperim.width - resized_img.width)   // 2
    y = (paperim.height - resized_img.height) // 2

    paperim.paste(resized_img, (x,y))  # Centered
    paperim.save(output_file,  'PDF', quality=100, resolution=max(x_dpi, y_dpi))

    if delete_it:
        os.remove(filename)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count")
    parser.add_argument("-c", "--cache", help="Use the cache, default false", action="store_true")
    parser.add_argument("-d", "--delete", help="Delete the source file (default_false)", action="store_true")
    parser.add_argument("-mx", "--margin-x", help="Margin X mm", action="store", default=0, type=float)
    parser.add_argument("-my", "--margin-y", help="Margin Y mm", action="store", default=0, type=float)
    parser.add_argument("-p", "--paper", help="Type of Paper (A4, A3, Legal, Letter) default A4", action="store", default='A4')
    parser.add_argument("input_dir", help="Input dir to process")
    args = parser.parse_args()

    extensions = ('.jpg','.png','.gif') #add your image extentions
    for filename in glob.iglob(args.input_dir + '**/**', recursive=True):
        file_name,extension = os.path.splitext(filename)

        if extension.lower() in extensions:
            print(filename)
            process(filename, file_name, extension, 
                    margin=(args.margin_x, args.margin_y), 
                    delete_it=args.delete, cache=args.cache,
                    paper=args.paper)



