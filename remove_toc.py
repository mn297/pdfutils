import sys
import os
from PyPDF2 import PdfReader, PdfWriter

def remove_toc_from_pdf(input_pdf_path, output_pdf_path):
    # Open the source PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    # Copy each page from the source PDF into the writer.
    # Note: This does not automatically copy document-level metadata such as outlines.
    for page in reader.pages:
        writer.add_page(page)
    
    # The table-of-contents (TOC) in many PDFs is stored in the catalog as an "/Outlines" entry.
    # Remove the /Outlines entry if it exists.
    if '/Outlines' in writer._root_object:
        del writer._root_object['/Outlines']
    
    # Optionally, remove the /PageMode setting that might force a bookmarks display.
    if '/PageMode' in writer._root_object:
        del writer._root_object['/PageMode']
    
    # Write the new PDF without TOC/outlines.
    with open(output_pdf_path, 'wb') as f_out:
        writer.write(f_out)

if __name__ == '__main__':
    # Expect exactly one argument: the input PDF path.
    if len(sys.argv) != 2:
        print("Usage: python remove_toc.py input.pdf")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    # Derive the output filename by appending '_tocless' before the file extension.
    base, ext = os.path.splitext(input_pdf)
    output_pdf = f"{base}_tocless{ext}"
    
    remove_toc_from_pdf(input_pdf, output_pdf)
    print(f"Created TOC-less PDF: {output_pdf}")
