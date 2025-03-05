import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
import concurrent.futures

# Constants
INPUT_DIR = "output/sources"  # Directory containing text files to process
OUTPUT_DIR = "transcripts"    # Directory to save generated transcripts
MAX_RETRIES = 3              # Maximum number of retries for API calls
RETRY_DELAY = 2              # Delay between retries in seconds
MAX_WORKERS = 5              # Maximum number of parallel workers

def init_gemini_client() -> None:
    """Initialize and configure the Gemini client."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)

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
        print(f"Error reading file {file_path}: {e}")
        return ""

def extract_topic(content: str, filename: str) -> str:
    """Extract topic from file content or filename."""
    # Try to get topic from the first line as a title
    first_line = content.strip().split('\n')[0] if content else ""
    if first_line:
        return first_line
    
    # Fallback to filename without extension and underscores
    return os.path.splitext(os.path.basename(filename))[0].replace('_', ' ')

def generate_transcript(content: str, topic: str) -> Optional[str]:
    """Generate educational transcript from content using Gemini API."""
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    You're creating an educational transcript for a video or podcast about: {topic}

    Please convert the following technical content into a natural, conversational transcript format.
    
    REQUIREMENTS:
    1. Include speaker indicators (Host, Expert, etc.)
    2. Format as a conversation between 2-3 experts discussing the topic
    3. Include all key information from the original content
    4. Use a friendly, educational tone that's easy to follow
    5. Add natural transitions, questions, and explanations between concepts
    6. Make the transcript feel like a real conversation, not just reading facts
    7. Include brief introductions of speakers at the beginning
    
    Here is the source content to convert:
    -----------
    {content}
    -----------
    
    Begin the transcript now:
    """
    
    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(prompt)
            if response.text:
                return response.text
            return None
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Failed to generate transcript after {MAX_RETRIES} attempts: {e}")
                return None

def save_transcript(transcript: str, output_path: str) -> None:
    """Save generated transcript to a file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(transcript)

def process_file(file_path: str, idx: int) -> Dict[str, Any]:
    """Process a single text file and generate transcript."""
    result = {"index": idx, "file_path": file_path, "success": False, "output_path": None}
    
    try:
        print(f"[{idx}] Processing: {os.path.basename(file_path)}")
        content = read_text_file(file_path)
        
        if not content:
            print(f"[{idx}] No content found in {file_path}")
            return result
        
        # Extract topic
        topic = extract_topic(content, file_path)
        
        # Generate transcript
        transcript = generate_transcript(content, topic)
        
        if not transcript:
            print(f"[{idx}] Failed to generate transcript for {os.path.basename(file_path)}")
            return result
        
        # Create output path
        filename = os.path.basename(file_path)
        output_path = os.path.join(OUTPUT_DIR, f"transcript_{os.path.splitext(filename)[0]}.txt")
        
        # Save transcript
        save_transcript(transcript, output_path)
        result["success"] = True
        result["output_path"] = output_path
        print(f"[{idx}] Successfully generated transcript for {os.path.basename(file_path)}")
        
    except Exception as e:
        print(f"[{idx}] Error processing file {file_path}: {e}")
    
    return result

def main():
    """Main function to process all text files in parallel."""
    start_time = time.time()
    
    try:
        print("Initializing Gemini client...")
        init_gemini_client()
        
        print(f"Getting text files from: {INPUT_DIR}")
        file_paths = get_text_files(INPUT_DIR)
        
        if not file_paths:
            print(f"No text files found in {INPUT_DIR}")
            return
        
        print(f"Found {len(file_paths)} text files to process")
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Process files in parallel
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_index = {
                executor.submit(process_file, file_path, i): i 
                for i, file_path in enumerate(file_paths)
            }
            
            for future in concurrent.futures.as_completed(future_to_index):
                result = future.result()
                results.append(result)
        
        # Count successful transcripts
        success_count = sum(1 for result in results if result["success"])
        
        # Report results
        print(f"\nProcessing complete: {success_count} of {len(file_paths)} transcripts generated successfully")
        print(f"Total processing time: {(time.time() - start_time):.2f} seconds")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()