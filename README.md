# VCProcessor
Converts from/to PDF/png, jpg, gif formats in order to build PDF booklets, managing paper sizes and some basic options.

## Tools

All Tools have been written on [Python 3.11](https://www.python.org/), and require
[PIL](https://pillow.readthedocs.io/en/stable/) and [PyMuPDF](https://github.com/pymupdf/PyMuPDF).

```bash
% python3 -m pip install --upgrade PyMuPDF
% python3 -m pip install --upgrade pip
% python3 -m pip install --upgrade Pillow
```

### img2pdf

Get a directory with image files, build a PDF with the paper size selected, at the required DPI. Useful to build booklets of previously extracted images (from PDF) or a list of images.

```
process(filename, fpath, fext, delete_it=False, margin=(0, 0), cache=True, paper='A4')
    generate the PDF file from an image file

    Args:
        filename (str): the full path to the image file
        fpath (str): the full path, without extension
        fext (str): file's extension (.jpg, .png)
        delete_it (bool, optional): delete the original file after processing. Defaults to False.
        margin (tuple, optional): X and Y margin, in mm. Defaults to (0,0).
        cache (bool, optional): If cache, don't create output the file if previously exists. Default=True.
        paper (str, optional): Size of the PDF paper. Defaults to 'A4'.
```


#### Usage:

```bash
% python.exe .\img2pdf.py -mx 7 -my 7 .\Croquis\Alicante\ -p A5
```

Creates the pdf for each files in the input directory, with a margin of 7mm in all sides, on a A5 page.

### pdf2img

Get a directory with PDF files, build a image file with the render of the PDF. Useful to build different paper versions of the PDF, o add margins later.

```
process(filename, fpath, fext, delete_it=False, cache=True, tag='exp')
    get a PDF, render it and save a high res version in PNG

    Args:
        filename (str): the full path to the image file
        fpath (str): the full path, without extension
        fext (str): file's extension (.jpg, .png)
        delete_it (bool, optional): delete the original file after processing. Defaults to False.
        cache (bool, optional): If cache, don't create output the file if previously exists. Default=True.
        tag (str, optional): Add the tag value inside the output file name. Defaults to 'exp'.
```

#### Usage:

```bash
% python.exe .\pdf2img.py -t a5 .\Croquis\Alicante\
```

Creates the image for each PDF found in `input directory`, and tags the output filename with `_a5_` in the middle (useful to find the new generated files). 


### gen_book

Get the files in the `input dir`, build a PDF book concatenating all the files. Created to build the VC booklet of info, so if you passed the -o switch, only process the official files (original info files.)

```
process(filelist, fname, vc_files=[])
    process the input file filelist and build the pdf booklet

    Args:
        filelist (list): list with the full path to the pdf files
        fname (str): output file name
        vc_files (list, optional): the original vc files. Defaults to [].
```

#### Usage:

```bash
% python.exe .\gen_book.py -o ".\Croquis\Madrid\Pedriza\Cancho de los Muertos" muertos.pdf
```

Creates a booklet called muertos.pdf, with only the original VC files, from the input dir.

