#!/usr/bin/env python3
import os
import logging
import time
from typing import List, Dict, Any
import concurrent.futures

from audio_maker.tts_generator import TTSGenerator, DEFAULT_LANG_CODE, DEFAULT_VOICE, DEFAULT_SPEED

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("transcript_to_audio")

# Configuration constants
TRANSCRIPTS_DIR = "output/transcripts"
AUDIOS_DIR = "output/audios"
MAX_WORKERS = 2  # Number of parallel workers for processing
SPLIT_PATTERN = r'\n\n+'  # Pattern to split transcripts into segments

def get_transcript_files(directory: str) -> List[str]:
    """
    Get all transcript files from the specified directory.
    
    Args:
        directory: Directory to search for transcript files
        
    Returns:
        List of file paths
    """
    if not os.path.exists(directory):
        logger.error(f"Directory doesn't exist: {directory}")
        raise ValueError(f"Directory doesn't exist: {directory}")
    
    file_paths = []
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            file_paths.append(os.path.join(directory, file))
    
    return sorted(file_paths)

def read_transcript(file_path: str) -> str:
    """
    Read content from a transcript file.
    
    Args:
        file_path: Path to the transcript file
        
    Returns:
        Content of the transcript file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise

def process_transcript(
    file_path: str, 
    output_dir: str, 
    tts_generator: TTSGenerator,
    idx: int = 0,
) -> Dict[str, Any]:
    """
    Process a transcript file and generate audio.
    
    Args:
        file_path: Path to the transcript file
        output_dir: Directory to save audio files
        tts_generator: TTSGenerator instance
        idx: Index for parallel processing
        
    Returns:
        Dictionary with processing results
    """
    result = {
        "index": idx,
        "file_path": file_path,
        "success": False,
        "output_files": []
    }
    
    try:
        logger.info(f"[{idx}] Processing transcript: {os.path.basename(file_path)}")
        
        # Read transcript content
        content = read_transcript(file_path)
        if not content:
            logger.warning(f"[{idx}] Empty transcript file: {file_path}")
            return result
        
        # Create base filename for audio
        filename = os.path.basename(file_path)
        base_filename = os.path.splitext(filename)[0]
        
        # Generate and save audio
        output_files = tts_generator.generate_and_save(
            content, 
            output_dir,
            base_filename,
            split_pattern=SPLIT_PATTERN
        )
        
        result["success"] = True
        result["output_files"] = output_files
        logger.info(f"[{idx}] Successfully generated audio for {os.path.basename(file_path)}")
        
    except Exception as e:
        logger.error(f"[{idx}] Error processing transcript {file_path}: {e}")
    
    return result

def process_transcripts_parallel(
    transcript_files: List[str], 
    output_dir: str, 
    tts_generator: TTSGenerator,
) -> List[Dict[str, Any]]:
    """
    Process transcript files in parallel.
    
    Args:
        transcript_files: List of transcript file paths
        output_dir: Directory to save audio files
        tts_generator: TTSGenerator instance
        
    Returns:
        List of dictionaries with processing results
    """
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_index = {
            executor.submit(
                process_transcript, 
                file_path, 
                output_dir, 
                tts_generator, 
                i
            ): i 
            for i, file_path in enumerate(transcript_files)
        }
        
        for future in concurrent.futures.as_completed(future_to_index):
            result = future.result()
            results.append(result)
    
    return results

def main():
    """Main function to process all transcript files and generate audio."""
    start_time = time.time()
    
    try:
        # Initialize TTS generator
        logger.info(f"Initializing TTS generator with language={DEFAULT_LANG_CODE}, voice={DEFAULT_VOICE}")
        tts_generator = TTSGenerator(
            lang_code=DEFAULT_LANG_CODE,
            voice=DEFAULT_VOICE,
            speed=DEFAULT_SPEED
        )
        
        # Get transcript files
        logger.info(f"Getting transcript files from: {TRANSCRIPTS_DIR}")
        transcript_files = get_transcript_files(TRANSCRIPTS_DIR)
        
        if not transcript_files:
            logger.warning(f"No transcript files found in {TRANSCRIPTS_DIR}")
            return
        
        logger.info(f"Found {len(transcript_files)} transcript files to process")
        
        # Create output directory if it doesn't exist
        os.makedirs(AUDIOS_DIR, exist_ok=True)
        
        # Process transcripts in parallel
        results = process_transcripts_parallel(
            transcript_files, 
            AUDIOS_DIR, 
            tts_generator
        )
        
        # Count successful generations
        success_count = sum(1 for result in results if result["success"])
        
        # Report results
        logger.info(f"\nProcessing complete: {success_count} of {len(transcript_files)} audios generated successfully")
        logger.info(f"Total processing time: {(time.time() - start_time):.2f} seconds")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()