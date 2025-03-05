import os
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PyPDF2 import PdfMerger

from dto import NotionPage
from font_manager import ensure_font_available

def page_to_pdf(page: NotionPage, output_dir: str = "output") -> str:
    """Convert a Notion page to PDF and return the file path."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a safe filename from the page title
    safe_title = "".join(c if c.isalnum() else "_" for c in page.title)
    pdf_path = os.path.join(output_dir, f"{safe_title}.pdf")
    
    # Ensure fonts are available
    if not ensure_font_available("DejaVuSans"):
        raise Exception("Required fonts could not be loaded")
    
    # Create PDF document with UTF-8 encoding
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Update styles to use Unicode font
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='DejaVuSans-Bold', encoding='UTF-8')
    heading1_style = ParagraphStyle('Heading1', parent=styles['Heading1'], fontName='DejaVuSans-Bold', encoding='UTF-8')
    paragraph_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='DejaVuSans', encoding='UTF-8')
    
    # Create indentation styles with proper font
    indent_styles = []
    for i in range(10):  # Support up to 10 levels of indentation
        indent_styles.append(ParagraphStyle(
            f'Indent{i}',
            parent=paragraph_style,
            leftIndent=i*20,  # Increase indentation by 20 points per level
            fontName='DejaVuSans',
            encoding='UTF-8'
        ))
    
    # Build PDF content
    content = []
    
    # Add title
    content.append(Paragraph(page.title, title_style))
    content.append(Spacer(1, 12))
    
    # Add blocks
    for block in page.blocks:
        style = None
        block_text = block.content
        
        # Choose style based on block type and indentation
        if block.type == 'heading_1':
            style = heading1_style
        elif block.type == 'heading_2':
            style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontName='DejaVuSans-Bold', encoding='UTF-8')
        elif block.type == 'heading_3':
            style = ParagraphStyle('Heading3', parent=styles['Heading3'], fontName='DejaVuSans-Bold', encoding='UTF-8')
        else:
            # Use indentation style based on indent level
            indent_level = min(block.indent_level, len(indent_styles) - 1)
            style = indent_styles[indent_level]
        
        # Add block type prefix for certain types
        if block.type not in ['heading_1', 'heading_2', 'heading_3', 'paragraph']:
            block_text = f"{block.type.capitalize()}: {block_text}"
        
        # Add paragraph to content
        content.append(Paragraph(block_text, style))
        content.append(Spacer(1, 6))
    
    # Build the PDF
    doc.build(content)
    print(f"Created PDF: {pdf_path}")
    
    return pdf_path

def merge_pdfs(pdf_paths: List[str], output_path: str = "output/combined.pdf") -> str:
    """Merge multiple PDFs into a single file."""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create PDF merger
    merger = PdfMerger()
    
    # Add each PDF to the merger
    for pdf_path in pdf_paths:
        merger.append(pdf_path)
    
    # Write the merged PDF to file
    merger.write(output_path)
    merger.close()
    
    print(f"Created combined PDF: {output_path}")
    return output_path