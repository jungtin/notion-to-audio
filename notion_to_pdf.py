import os
from dotenv import load_dotenv
from notion_client import Client
from typing import Dict, Any, List, TypedDict
import json
from dataclasses import dataclass
# Import libraries for PDF generation and merging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PyPDF2 import PdfMerger
import tempfile
# Add these imports for font support
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# Add imports for font download and management
import requests
import shutil
from pathlib import Path

@dataclass
class NotionBlock:
    type: str
    content: str
    indent_level: int
    has_children: bool

@dataclass
class NotionPage:
    id: str
    title: str
    blocks: List[NotionBlock]

def init_notion_client() -> Client:
    """Initialize and return the Notion client."""
    load_dotenv()
    notion_api_key = os.getenv("NOTION_API_KEY")
    
    if not notion_api_key:
        raise ValueError("NOTION_API_KEY not found in environment variables")
    
    return Client(auth=notion_api_key)

def get_database_pages(notion: Client, database_id: str) -> list[Dict[str, Any]]:
    """Retrieve all pages from the specified database, sorted by their order."""
    try:
        # Query the database with sorting
        response = notion.databases.query(
            database_id=database_id,
            sorts=[{
                "timestamp": "created_time",
                "direction": "ascending"
            }]
        )
        return response.get("results", [])
    except Exception as e:
        print(f"Error querying database: {e}")
        return []

def extract_block_content(block: Dict[str, Any]) -> str:
    """Extract content from a block based on its type."""
    block_type = block.get("type", "")
    if not block_type in block:
        return ""

    block_data = block[block_type]

    # Handle different block types
    if "rich_text" in block_data:
        text_content = [text.get("plain_text", "") for text in block_data["rich_text"]]
        return " ".join(text_content)
    elif "text" in block_data:
        text_content = [text.get("plain_text", "") for text in block_data["text"]]
        return " ".join(text_content)
    elif block_type == "child_page":
        return block_data.get("title", "")
    
    return ""

def extract_blocks(notion: Client, page_id: str, indent: int = 0) -> List[NotionBlock]:
    """Recursively extract blocks and their children."""
    result_blocks = []
    api_blocks = notion.blocks.children.list(block_id=page_id).get("results", [])
    
    for block in api_blocks:
        block_type = block.get("type", "")
        content = extract_block_content(block)
        has_children = block.get("has_children", False)
        
        if content:
            result_blocks.append(NotionBlock(
                type=block_type,
                content=content,
                indent_level=indent,
                has_children=has_children
            ))
        
        if has_children:
            # child_indent = indent + 1 if block_type == "toggle" else indent
            child_indent = indent + 1
            result_blocks.extend(extract_blocks(notion, block["id"], child_indent))
    
    return result_blocks

def extract_page_content(notion: Client, page: Dict[str, Any]) -> NotionPage:
    """Extract all content from a page and return structured data."""
    try:
        page_id = page["id"]
        page_title = page.get("properties", {}).get("Name", {}).get("title", [{}])[0].get("plain_text", "Untitled")
        blocks = extract_blocks(notion, page_id)
        
        return NotionPage(
            id=page_id,
            title=page_title,
            blocks=blocks
        )
    
    except Exception as e:
        print(f"Error processing page: {e}")
        return NotionPage(id="", title="Error", blocks=[])

def print_page(page: NotionPage) -> None:
    """Print the page content in a formatted way."""
    print(f"\n{'='*50}")
    print(f"Page: {page.title}")
    print(f"ID: {page.id}\n")
    
    for block in page.blocks:
        indent_str = "  - " * block.indent_level
        # print(f"{indent_str}{block.type.capitalize()}: {block.content}")

def ensure_font_available(font_name="DejaVuSans", font_url=None):
    """Ensures that the required font is available for use."""
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    
    font_files = {
        "DejaVuSans": {
            "regular": {
                "path": os.path.join(fonts_dir, "DejaVuSans.ttf"),
                "url": "https://downloads.sourceforge.net/project/dejavu/dejavu/2.37/dejavu-fonts-ttf-2.37.tar.bz2"
            },
            "bold": {
                "path": os.path.join(fonts_dir, "DejaVuSans-Bold.ttf"),
                "url": "https://downloads.sourceforge.net/project/dejavu/dejavu/2.37/dejavu-fonts-ttf-2.37.tar.bz2"
            }
        }
    }
    
    # Download and save fonts if they don't exist
    # Check if any font in the font family needs to be downloaded
    need_download = False
    for style, font_info in font_files.get(font_name, {}).items():
        if not os.path.exists(font_info["path"]):
            need_download = True
            break
    
    # Download and extract the archive only once if any font is missing
    if need_download:
        try:
            import tempfile
            import tarfile
            
            # Get URL from the first font (they're all the same archive)
            url = next(iter(font_files.get(font_name, {}).values()))["url"]
            print(f"Downloading {font_name} fonts archive...")
            
            # Download the archive to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".tar.bz2", delete=False) as temp_file:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, temp_file)
                archive_path = temp_file.name
            
            # Extract the required font files
            with tarfile.open(archive_path, "r:bz2") as tar:
                for style, font_info in font_files.get(font_name, {}).items():
                    font_filename = os.path.basename(font_info["path"])
                    # Find the TTF file in the archive
                    for member in tar.getmembers():
                        if member.name.endswith(font_filename):
                            # Extract the font file
                            f = tar.extractfile(member)
                            with open(font_info["path"], 'wb') as font_file:
                                shutil.copyfileobj(f, font_file)
                            print(f"Extracted {font_name} {style} font to {font_info['path']}")
                            break
            
            # Clean up
            os.unlink(archive_path)
        except Exception as e:
            print(f"Error downloading or extracting fonts: {e}")
            return False
    
    # Now check that all fonts exist after download attempt
    for style, font_info in font_files.get(font_name, {}).items():
        font_path = font_info["path"]
        if not os.path.exists(font_path):
            print(f"Font file not found: {font_path}")
            return False
        print(f"Using {font_name} {style} font: {font_path}")
    
    # Register fonts with reportlab
    try:
        if "DejaVuSans" not in pdfmetrics._fonts:
            # Register both original case and lowercase versions for regular font
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_files["DejaVuSans"]["regular"]["path"]))
            pdfmetrics.registerFont(TTFont('dejavusans', font_files["DejaVuSans"]["regular"]["path"]))
            
            # Register both original case and lowercase versions for bold font
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_files["DejaVuSans"]["bold"]["path"]))
            pdfmetrics.registerFont(TTFont('dejavusans-bold', font_files["DejaVuSans"]["bold"]["path"]))
        return True
    except Exception as e:
        print(f"Error registering fonts: {e}")
        return False

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

def main():
    """Main function to process the Notion database."""
    try:
        notion = init_notion_client()
        database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not database_id:
            raise ValueError("NOTION_DATABASE_ID not found in environment variables")
        
        print("Fetching database pages...")
        pages = get_database_pages(notion, database_id)
        
        if not pages:
            print("No pages found in the database.")
            return
        
        print(f"Found {len(pages)} pages in the database.")
        
        # Process all pages and convert to PDFs
        pdf_paths = []
        for page_data in pages:
            page = extract_page_content(notion, page_data)
            print_page(page)
            
            # Convert page to PDF
            pdf_path = page_to_pdf(page)
            pdf_paths.append(pdf_path)
            
        
        # Merge all PDFs into one file
        if pdf_paths:
            merged_pdf = merge_pdfs(pdf_paths)
            print(f"\nAll pages have been successfully converted to PDF and merged into {merged_pdf}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
