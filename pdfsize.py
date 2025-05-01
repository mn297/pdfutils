#!/usr/bin/env python3
import sys
from PyPDF2 import PdfReader, PdfWriter, Transformation

# Usage:
# python resize_pdf.py input.pdf output.pdf
if len(sys.argv) != 3:
    print("Usage: python resize_pdf.py input.pdf output.pdf")
    sys.exit(1)

input_pdf_path = sys.argv[1]
output_pdf_path = sys.argv[2]

# Open the input PDF for reading.
reader = PdfReader(input_pdf_path)
writer = PdfWriter()

# Use the first page as the reference for the target page size.
ref_page = reader.pages[0]
ref_width = float(ref_page.mediabox.width)
ref_height = float(ref_page.mediabox.height)
print(f"Reference page size: {ref_width} x {ref_height} pts")

# Process each page: scale page content to fit the reference size and update mediabox.
for idx, page in enumerate(reader.pages):
    # Get current page dimensions.
    cur_width = float(page.mediabox.width)
    cur_height = float(page.mediabox.height)
    print(f"Page {idx+1}: original size = {cur_width} x {cur_height} pts")
    
    # Compute uniform scaling factor so that content fits within the reference size.
    scale_factor = min(ref_width / cur_width, ref_height / cur_height)
    new_width = cur_width * scale_factor
    new_height = cur_height * scale_factor
    
    # Compute translation offsets to center the scaled content.
    tx = (ref_width - new_width) / 2
    ty = (ref_height - new_height) / 2
    print(f"Page {idx+1}: scale factor = {scale_factor:.4f}, translation = ({tx:.2f}, {ty:.2f})")
    
    # Build and apply the transformation: scale then translate.
    transformation = Transformation().scale(scale_factor).translate(tx, ty)
    page.add_transformation(transformation)
    
    # Update the page mediabox to match the reference dimensions.
    page.mediabox.lower_left = (0, 0)
    page.mediabox.upper_right = (ref_width, ref_height)
    
    # Add the modified page to the writer.
    writer.add_page(page)

# Recursive function to copy the document outline.
def copy_outline(items, parent=None):
    for item in items:
        # Each outline item has a title.
        title = item.title
        try:
            # Get the destination page number (zero-indexed) from the outline item.
            pagenum = reader.get_destination_page_number(item)
        except Exception as e:
            print(f"Error getting destination for outline item '{title}': {e}")
            continue

        # Add the outline item to the writer.
        new_item = writer.add_outline_item(title, pagenum, parent=parent)
        
        # If this outline item has children, process them recursively.
        children = getattr(item, "children", None)
        if children:
            copy_outline(children, parent=new_item)

# Attempt to retrieve the document outline (bookmarks) via the new attribute.
try:
    outline = reader.document_outline
    copy_outline(outline)
except Exception as e:
    print("Error copying document outline:", e)

# Write the output PDF.
with open(output_pdf_path, "wb") as out_f:
    writer.write(out_f)

print("Resizing complete. Output saved to", output_pdf_path)
