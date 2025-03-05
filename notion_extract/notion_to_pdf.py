import os
import threading
import concurrent.futures
from dotenv import load_dotenv

# Import from our new modules
from notion_extract.helper.notion_service import init_notion_client, get_database_pages, extract_page_content, print_page
from notion_extract.helper.pdf_generator import page_to_pdf, merge_pdfs, clean_output_directory

OUTPUT_DIR = "output/pdf"

def process_page(notion, page_data, index):
    """Process a single page and return its data along with the original index"""
    try:
        page = extract_page_content(notion, page_data)
        # print_page(page)
        
        # Convert page to PDF
        pdf_path = page_to_pdf(page, OUTPUT_DIR)
        return {
            "index": index,
            "pdf_path": pdf_path,
            "page_title": page.title
        }
    except Exception as e:
        print(f"Error processing page: {e}")
        return {
            "index": index,
            "pdf_path": None,
            "page_title": f"Error processing page {index}"
        }

def main():
    """Main function to process the Notion database."""
    try:
        notion = init_notion_client()
        database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not database_id:
            raise ValueError("NOTION_DATABASE_ID not found in environment variables")
        
        clean_output_directory(OUTPUT_DIR)
        
        print("Fetching database pages...")
        pages_data = get_database_pages(notion, database_id)
        
        if not pages_data:
            print("No pages found in the database.")
            return
        
        print(f"Found {len(pages_data)} pages in the database.")
        
        # Process pages in parallel using ThreadPoolExecutor
        print("Processing pages in parallel...")
        results = []
        
        # Use ThreadPoolExecutor to process pages in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all tasks and keep track of the futures
            future_to_index = {
                executor.submit(process_page, notion, page_data, i): i 
                for i, page_data in enumerate(pages_data)
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_index):
                result = future.result()
                results.append(result)
                if result["pdf_path"]:
                    print(f"Completed processing page: {result['page_title']}")
                else:
                    print(f"Failed to process page at index {result['index']}")
        
        # Sort results by their original index to maintain order
        results.sort(key=lambda x: x["index"])
        
        # Extract PDF paths in the correct order
        pdf_paths = [result["pdf_path"] for result in results if result["pdf_path"] is not None]
        
        # Merge all PDFs into one file, preserving order
        if pdf_paths:
            merged_pdf = merge_pdfs(pdf_paths, OUTPUT_DIR + "/combined.pdf")
            print(f"\nAll pages have been successfully converted to PDF and merged into {merged_pdf}")
        else:
            print("No PDFs were successfully created.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
