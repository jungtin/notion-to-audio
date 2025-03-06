import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Optional
import concurrent.futures
import threading
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transcript_maker.prompt import create_educational_transcript_prompt

# Constants
INPUT_DIR = "output/txt/sources"  # Directory containing text files to process
OUTPUT_DIR = "output/transcripts-parallel"    # Directory to save generated transcripts
MAX_RETRIES = 3              # Maximum number of retries for API calls
RETRY_DELAY = 2              # Delay between retries in seconds
MAX_CHUNK_SIZE = 6000        # Maximum size of content chunks (in characters)
OVERLAP_SIZE = 200           # Overlap between chunks to maintain context
MAX_THREADS = 2              # Maximum number of concurrent threads

# Thread-local storage for the Gemini model
thread_local = threading.local()

def get_worker_id():
    """Get a short identifier for the current thread."""
    return f"Worker-{threading.current_thread().name.split('-')[-1]}"

def init_gemini_client() -> None:
    """Initialize and configure the Gemini client."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)

def get_model():
    """Get or create a thread-local Gemini model instance."""
    if not hasattr(thread_local, "model"):
        thread_local.model = genai.GenerativeModel('gemini-2.0-flash')
    return thread_local.model

def get_text_files(directory: str) -> List[str]:
    """Get all text files from the specified directory."""
    if not os.path.exists(directory):
        raise ValueError(f"Directory doesn't exist: {directory}")
    
    file_paths = []
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            file_paths.append(os.path.join(directory, file))
    
    return file_paths

def read_text_file(file_path: str) -> str:
    """Read content from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f" Error reading file {file_path}: {e}")
        return ""

def extract_topic(content: str, filename: str) -> str:
    """Extract topic from file content or filename."""
    # Try to get topic from the first line as a title
    first_line = content.strip().split('\n')[0] if content else ""
    if first_line:
        return first_line
    
    # Fallback to filename without extension and underscores
    return os.path.splitext(os.path.basename(filename))[0].replace('_', ' ')

def split_content(content: str) -> List[str]:
    """Split content into smaller chunks using LangChain's recursive text splitter."""
    if len(content) <= MAX_CHUNK_SIZE:
        return [content]
    
    # Initialize the recursive text splitter with appropriate parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CHUNK_SIZE,
        chunk_overlap=OVERLAP_SIZE,
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
    )
    
    # Split the content
    chunks = text_splitter.split_text(content)
    
    return chunks

def generate_transcript_chunk(content: str, topic: str, part_number: int = 0, total_parts: int = 1) -> Optional[str]:
    """Generate transcript for a chunk of content."""
    model = get_model()
    
    part_info = ""
    if total_parts > 1:
        part_info = f"\nThis is part {part_number + 1} of {total_parts} of the content."
    
    prompt = create_educational_transcript_prompt(topic, content, part_number, total_parts, part_info)
    
    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(prompt)
            if response.text:
                return response.text
            return None
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"[{topic}] Attempt {attempt + 1} failed: {e}. Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"[{topic}] Failed to generate transcript after {MAX_RETRIES} attempts: {e}")
                return None

def generate_transcript(content: str, topic: str) -> Optional[str]:
    """Generate educational transcript from content using Gemini API.
    Handles large content by splitting into multiple requests if needed."""
    # Split content into chunks if it's too large
    content_chunks = split_content(content)
    
    if len(content_chunks) == 1:
        # If there's only one chunk, use the original method
        return generate_transcript_chunk(content, topic)
    
    # For multiple chunks, process each one and combine results
    print(f"[{topic}] Content split into {len(content_chunks)} chunks due to size")
    transcript_parts = []
    
    for i, chunk in enumerate(content_chunks):
        print(f"[{topic}] Processing chunk {i+1}/{len(content_chunks)}...")
        transcript_part = generate_transcript_chunk(chunk, topic, i, len(content_chunks))
        
        if not transcript_part:
            print(f"[{topic}] Failed to generate transcript for chunk {i+1}")
            return None
        
        transcript_parts.append(transcript_part)
        # Add a small delay between API calls to avoid rate limits
        if i < len(content_chunks) - 1:
            time.sleep(1)
    
    # Combine all parts into a single transcript
    return "\n\n".join(transcript_parts)

def save_transcript(transcript: str, output_path: str) -> None:
    """Save generated transcript to a file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(transcript)
    
    print(f" Transcript saved to: {output_path}")

def process_file(file_path: str) -> bool:
    """Process a single text file and generate transcript."""
    try:
        print(f"Processing: {file_path}")
        content = read_text_file(file_path)
        
        if not content:
            print(f" No content found in {file_path}")
            return False
        
        # Extract topic
        topic = extract_topic(content, file_path)
        print(f" Topic identified: {topic}")
        
        # Generate transcript
        transcript = generate_transcript(content, topic)
        
        if not transcript:
            print(f"[{topic}] Failed to generate transcript for {file_path}")
            return False
        
        # Create output path
        filename = os.path.basename(file_path)
        output_path = os.path.join(OUTPUT_DIR, f"transcript_{os.path.splitext(filename)[0]}.txt")
        
        # Save transcript
        save_transcript(transcript, output_path)
        return True
        
    except Exception as e:
        print(f" Error processing file {file_path}: {e}")
        return False

def main():
    """Main function to process all text files concurrently using threads."""
    try:
        print("Initializing Gemini client...")
        init_gemini_client()
        
        print(f"Getting text files from: {INPUT_DIR}")
        file_paths = get_text_files(INPUT_DIR)
        
        if not file_paths:
            print(f"No text files found in {INPUT_DIR}")
            return
        
        print(f"Found {len(file_paths)} text files to process")
        print(f"Processing files with up to {MAX_THREADS} concurrent threads\n\n")
        print("=========================================\n\n")
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Create a thread pool and submit all files for processing
        success_count = 0
        failed_files = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            # Submit all tasks and store future objects with their file paths
            future_to_file = {executor.submit(process_file, file_path): file_path for file_path in file_paths}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    if future.result():
                        success_count += 1
                    else:
                        failed_files.append(os.path.basename(file_path))
                except Exception as e:
                    print(f"Error in thread processing {file_path}: {e}")
                    failed_files.append(os.path.basename(file_path))
        
        print(f"\nProcessing complete: {success_count} of {len(file_paths)} transcripts generated successfully")
        
        if failed_files:
            print(f"Failed files: {', '.join(failed_files)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()