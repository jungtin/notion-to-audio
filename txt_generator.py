import os
import shutil
from typing import List
from dto import NotionPage

def clean_output_directory(output_dir: str = "output") -> None:
    """
    Cleans the output directory by removing all files and subdirectories.
    Creates the directory if it doesn't exist.
    
    Args:
        output_dir: Path to the output directory to clean
    """
    
    # Check if directory exists
    if os.path.exists(output_dir):
        print(f"Cleaning output directory: {output_dir}")
        # Remove all contents
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
    else:
        print(f"Creating output directory: {output_dir}")
        
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)

def page_to_txt(page: NotionPage, output_dir: str, index: int) -> str:
    """Convert a Notion page to TXT and return the file path."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(output_dir, "sources")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a safe filename from the page title
    safe_title = "".join(c if c.isalnum() else "_" for c in page.title)
    txt_path = os.path.join(output_dir, f"{index} - {safe_title}.txt")
    
    # Open text file and write content
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        # Write title
        txt_file.write(f"{page.title}\n")
        txt_file.write("=" * len(page.title) + "\n\n")
        
        # Process blocks
        for block in page.blocks:
            # Add indentation
            indent = "    " * block.indent_level
            
            # Format block based on type
            if block.type == 'heading_1':
                txt_file.write(f"\n{block.content}\n")
                txt_file.write("-" * len(block.content) + "\n")
            elif block.type == 'heading_2':
                txt_file.write(f"\n{indent}{block.content}\n")
                txt_file.write(f"{indent}" + "-" * len(block.content) + "\n")
            elif block.type == 'heading_3':
                txt_file.write(f"\n{indent}{block.content}\n")
                txt_file.write(f"{indent}" + "~" * len(block.content) + "\n")
            elif block.type == 'bulleted_list_item':
                txt_file.write(f"{indent}• {block.content}\n")
            elif block.type == 'numbered_list_item':
                txt_file.write(f"{indent}* {block.content}\n")
            elif block.type == 'toggle':
                txt_file.write(f"{indent}▶ {block.content}\n")
            elif block.type == 'quote':
                txt_file.write(f"{indent}> {block.content}\n")
            elif block.type == 'code':
                txt_file.write(f"{indent}```\n{indent}{block.content}\n{indent}```\n")
            elif block.type == 'to_do':
                txt_file.write(f"{indent}□ {block.content}\n")
            else:
                txt_file.write(f"{indent}{block.content}\n")
            
            # Add spacing between paragraphs
            if block.type not in ['bulleted_list_item', 'numbered_list_item']:
                txt_file.write("\n")
    
    return txt_path

def merge_txt_files(txt_paths: List[str], output_path: str = "combined.txt") -> str:
    """Merge multiple text files into a single file."""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create a combined text file
    with open(output_path, 'w', encoding='utf-8') as outfile:
        # Process each text file
        for i, txt_path in enumerate(txt_paths):
            # Add a separator between files (except for the first one)
            if i > 0:
                outfile.write("\n\n" + "=" * 80 + "\n\n")
            
            # Read and append the content of each file
            with open(txt_path, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
    
    print(f"Created combined text file: {output_path}")
    return output_path