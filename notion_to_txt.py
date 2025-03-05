import os
import concurrent.futures
from dotenv import load_dotenv

# Import from our modules
from notion_service import init_notion_client, get_database_pages, extract_page_content, print_page
from txt_generator import page_to_txt, merge_txt_files, clean_output_directory

OUTPUT_DIR = "output_txt"

def process_page(notion, page_data, index):
    """Process a single page and return its data along with the original index"""
    try:
        page = extract_page_content(notion, page_data)
        # print_page(page)
        
        # Convert page to text file
        txt_path = page_to_txt(page, OUTPUT_DIR)
        return {
            "index": index,
            "txt_path": txt_path,
            "page_title": page.title
        }
    except Exception as e:
        print(f"Error processing page: {e}")
        return {
            "index": index,
            "txt_path": None,
            "page_title": f"Error processing page {index}"
        }

def main():
    """Main function to process the Notion database and export to text files."""
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
                if result["txt_path"]:
                    print(f"Completed processing page to text: {result['page_title']}")
                else:
                    print(f"Failed to process page at index {result['index']}")
        
        # Sort results by their original index to maintain order
        results.sort(key=lambda x: x["index"])
        
        # Extract text file paths in the correct order
        txt_paths = [result["txt_path"] for result in results if result["txt_path"] is not None]
        
        # Merge all text files into one file, preserving order
        if txt_paths:
            merged_txt = merge_txt_files(txt_paths, OUTPUT_DIR + "/combined.txt")
            print(f"\nAll pages have been successfully converted to text and merged into {merged_txt}")
        else:
            print("No text files were successfully created.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()