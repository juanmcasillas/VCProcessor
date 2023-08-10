from pdf2image import convert_from_path
import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
import fitz
import pikepdf
import os
import sys
import argparse
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2 import generic
from PyPDF2.generic import ContentStream
from PyPDF2.generic import TextStringObject, NameObject
import argparse


def extract_pages_1(fname):
    # Store Pdf with convert_from_path function
    images = convert_from_path(fname)
    
    for i in range(len(images)):
    
        # Save pages as images in the pdf
        images[i].save('page'+ str(i) +'.jpg', 'JPEG')
        
def extract_pages_2(fname):
    pdf = pdfium_c.FPDF_LoadDocument(fname.encode('utf-8'), None)
    pdf = pdfium.PdfDocument(fname)
    print(pdf)
    n_pages = len(pdf)
    for page_number in range(n_pages):
        page = pdf.get_page(page_number)
        pil_image = page.render_topil(
            scale=1,
            rotation=0,
            crop=(0, 0, 0, 0),
            colour=(255, 255, 255, 255),
            annotations=True,
            greyscale=False,
            optimise_mode=pdfium.OptimiseMode.NONE,
        )
        pil_image.save(f"image_{page_number+1}.png")

def extract_pages_3(fname):

    pdffile = fname
    doc = fitz.open(pdffile)
    zoom = 4
    mat = fitz.Matrix(zoom, zoom)
    count = 0
    # Count variable is to get the number of pages in the pdf
    for p in doc:
        print(p)
        count += 1
    for i in range(count):
        val = f"image_{i+1}.png"
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat)
        pix.save(val)
    doc.close()    

def extract_pages_4(fname):
    print("Processing {0}".format(fname))
    pdf = pikepdf.Pdf.open(fname, attempt_recovery=False, ignore_xref_streams=True)
    print(pdf)
    lastPageNum = len(pdf.pages)
    pdf.pages.remove(p = lastPageNum)
    #pdf.save(fname + '.tmp')
    pdf.close()
    #os.unlink(fname)
    #os.rename(fname + '.tmp', fname)

def uncompress(fname):


    pdf = PdfReader(fname)  
    pdf_writer = PdfWriter()

    for n in range(0, len(pdf.pages)):
        page = pdf.getPage(n)
        content_object = page["/Contents"].getObject()
        content = ContentStream(content_object, pdf)
        page.__setitem__(NameObject("/Contents"), content)
        pdf_writer.addPage(page)
    
    with Path("output.pdf").open(mode="wb") as output_file:
        pdf_writer.write(output_file)

def add_eof(fname):
    EOF_MARKER = b'%%EOF'


    with open(fname, 'rb') as f:
        contents = f.read()

    # check if EOF is somewhere else in the file
    if EOF_MARKER in contents:
        # we can remove the early %%EOF and put it at the end of the file
        contents = contents.replace(EOF_MARKER, b'')
        contents = contents + EOF_MARKER
    else:
        # Some files really don't have an EOF marker
        # In this case it helped to manually review the end of the file
        print(contents[-8:]) # see last characters at the end of the file
        # printed b'\n%%EO%E'
        contents = contents[:-6] + EOF_MARKER

    #with open(fname.replace('.pdf', '') + '_fixed.pdf', 'wb') as f:
    with open(fname, 'wb') as f:
        f.write(contents)

def add_eof_2(fname):
    NEWLINE = '\n' # 10 \r\n
    CR = "\r"   # 13

    with open(fname, 'ab') as f:
        f.write(b'\r\nendstream')
        f.write(b'\r\nendobj')
        f.write(b'\r\nxref')
        f.write(b'\r\n0 2')
        f.write(b'\r\n0000000000 65535 f')
        f.write(b'\r\n0000000000 00000 n')
        f.write(b'\r\ntrailer')
        f.write(b'\r\n<<')
        f.write(b'\r\n/Size 2')
        f.write(b'\r\n/ID [<28bf4e5e4e758a4164004e56fffa0108><28bf4e5e4e758a4164004e56fffa0108>]')
        f.write(b'\r\n>>')
        f.write(b'\r\nstartxref')
        f.write(b'\r\n143')
        f.write(b'\r\n%%EOF')
    
if __name__ == "__main__":
    add_eof_2(sys.argv[1])
    #uncompress(sys.argv[1])
    extract_pages_4(sys.argv[1])