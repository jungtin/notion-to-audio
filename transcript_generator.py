import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Optional

# Constants
INPUT_DIR = "output_txt/sources"  # Directory containing text files to process
OUTPUT_DIR = "transcripts"    # Directory to save generated transcripts
MAX_RETRIES = 3              # Maximum number of retries for API calls
RETRY_DELAY = 2              # Delay between retries in seconds

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
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    You're creating an educational transcript for a video or podcast about: {topic}

    Please convert the following technical content into a natural, conversational transcript format.
    
    REQUIREMENTS:
    1. Include all key information from the original content
    2. Use a friendly, educational tone that's easy to follow
    3. Add natural transitions, questions, and explanations between concepts
    4. Make the transcript feel like a real conversation, not just reading facts
    5. The transcript must be write in English
    6. Remove the code snippets and focus in the explanation of the concepts, code snippets can be replaced by a brief explanation of the code.
    7. Start explaining with the question WHY
    
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
    
    print(f"Transcript saved to: {output_path}")

def process_file(file_path: str) -> bool:
    """Process a single text file and generate transcript."""
    try:
        print(f"Processing: {file_path}")
        content = read_text_file(file_path)
        
        if not content:
            print(f"No content found in {file_path}")
            return False
        
        # Extract topic
        topic = extract_topic(content, file_path)
        print(f"Topic identified: {topic}")
        
        # Generate transcript
        transcript = generate_transcript(content, topic)
        
        if not transcript:
            print(f"Failed to generate transcript for {file_path}")
            return False
        
        # Create output path
        filename = os.path.basename(file_path)
        output_path = os.path.join(OUTPUT_DIR, f"transcript_{os.path.splitext(filename)[0]}.txt")
        
        # Save transcript
        save_transcript(transcript, output_path)
        return True
        
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False

def main():
    """Main function to process all text files."""
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
        
        # Process each file
        success_count = 0
        for file_path in file_paths:
            if process_file(file_path):
                success_count += 1
                break
        
        print(f"\nProcessing complete: {success_count} of {len(file_paths)} transcripts generated successfully")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()