#!/usr/bin/env python3
import os
import sys
import argparse
import importlib
import logging
from typing import List, Dict, Any, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("main")

def print_header() -> None:
    """Print application header."""
    print("\n" + "=" * 60)
    print("NOTION PDF CONTENT EXTRACTOR AND PROCESSOR".center(60))
    print("=" * 60)

def print_menu(options: Dict[str, str]) -> None:
    """Print the menu options."""
    print("\nPlease select an option:")
    for key, value in options.items():
        print(f"{key}. {value}")
    print("q. Quit")

def run_notion_extraction() -> None:
    """Run the Notion extraction process with submenu."""
    submenu_options = {
        "1": "Export Notion to PDF",
        "2": "Export Notion to Text",
        "3": "Return to main menu"
    }
    
    while True:
        print("\n--- Notion Extraction Options ---")
        print_menu(submenu_options)
        
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == "1":
            print("\nExporting Notion content to PDF...")
            try:
                from notion_extract import notion_to_pdf
                importlib.reload(notion_to_pdf)  # Ensure fresh module
                notion_to_pdf.main()
                print("\nNotion to PDF export completed!")
            except Exception as e:
                logger.error(f"Failed to export Notion to PDF: {e}")
        
        elif choice == "2":
            print("\nExporting Notion content to Text...")
            try:
                from notion_extract import notion_to_txt
                importlib.reload(notion_to_txt)  # Ensure fresh module
                notion_to_txt.main()
                print("\nNotion to Text export completed!")
            except Exception as e:
                logger.error(f"Failed to export Notion to Text: {e}")
        
        elif choice == "3" or choice == "b":
            break
        
        elif choice == "q":
            sys.exit(0)
        
        else:
            print("\nInvalid option. Please try again.")

def run_transcript_generation() -> None:
    """Run the transcript generation process."""
    print("\nGenerating transcripts from source files...")
    try:
        from transcript_maker import transcript_generator
        importlib.reload(transcript_generator)  # Ensure fresh module
        transcript_generator.main()
        print("\nTranscript generation completed!")
    except Exception as e:
        logger.error(f"Failed to generate transcripts: {e}")

def run_audio_generation() -> None:
    """Run the audio generation process."""
    print("\nGenerating audio from transcripts...")
    try:
        from audio_maker import transcript_to_audio
        importlib.reload(transcript_to_audio)  # Ensure fresh module
        transcript_to_audio.main()
        print("\nAudio generation completed!")
    except Exception as e:
        logger.error(f"Failed to generate audio: {e}")

def run_full_workflow() -> None:
    """Run the complete workflow: Notion extraction, transcript generation, and audio creation."""
    print("\nRunning complete workflow...")
    
    # Step 1: Notion extraction to text
    print("\n[Step 1/3] Extracting content from Notion...")
    try:
        from notion_extract import notion_to_txt
        importlib.reload(notion_to_txt)
        notion_to_txt.main()
        print("✓ Notion extraction completed!")
    except Exception as e:
        logger.error(f"Failed during Notion extraction: {e}")
        return
    
    # Step 2: Generate transcripts
    print("\n[Step 2/3] Generating transcripts...")
    try:
        from transcript_maker import transcript_generator
        importlib.reload(transcript_generator)
        transcript_generator.main()
        print("✓ Transcript generation completed!")
    except Exception as e:
        logger.error(f"Failed during transcript generation: {e}")
        return
    
    # Step 3: Generate audio
    print("\n[Step 3/3] Creating audio files...")
    try:
        from audio_maker import transcript_to_audio
        importlib.reload(transcript_to_audio)
        transcript_to_audio.main()
        print("✓ Audio generation completed!")
    except Exception as e:
        logger.error(f"Failed during audio generation: {e}")
        return
    
    print("\n✓ Complete workflow finished successfully!")

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Notion PDF Content Extractor and Processor")
    parser.add_argument("--extract", action="store_true", help="Run Notion extraction")
    parser.add_argument("--transcript", action="store_true", help="Run transcript generation")
    parser.add_argument("--audio", action="store_true", help="Run audio generation")
    parser.add_argument("--full", action="store_true", help="Run the full workflow")
    return parser.parse_args()

def main() -> None:
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # If arguments provided, run specific tasks
    if args.extract:
        run_notion_extraction()
        return
    elif args.transcript:
        run_transcript_generation()
        return
    elif args.audio:
        run_audio_generation()
        return
    elif args.full:
        run_full_workflow()
        return
        
    # No arguments provided, show interactive menu
    main_options = {
        "1": "Extract content from Notion",
        "2": "Generate transcripts from source files",
        "3": "Create audio from transcripts",
        "4": "Run the complete workflow"
    }
    
    print_header()
    
    while True:
        print_menu(main_options)
        
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == "1":
            run_notion_extraction()
        elif choice == "2":
            run_transcript_generation()
        elif choice == "3":
            run_audio_generation()
        elif choice == "4":
            run_full_workflow()
        elif choice == "q":
            print("\nExiting. Goodbye!")
            break
        else:
            print("\nInvalid option. Please try again.")

if __name__ == "__main__":
    main()