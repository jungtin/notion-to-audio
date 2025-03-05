import os
from dotenv import load_dotenv

# Import from our new modules
from notion_service import init_notion_client, get_database_pages, extract_page_content, print_page
from pdf_generator import page_to_pdf, merge_pdfs

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
