# Notion Content Extraction and Audio Generation

This repository provides a complete workflow for extracting content from Notion databases, processing it into transcripts using language models, and converting those transcripts into audio files. The project is organized into packages for better code structure and modularity.

## Main Features

### 1. Notion Content Extraction (`notion_extract`)
- **PDF Export**: Export all pages from a Notion database to PDF format and merge them into a single file
- **Text Export**: Extract raw text content from Notion pages for further processing

### 2. Transcript Generation (`transcript_maker`)
- Process raw text extracted from Notion
- Utilize LLM (Large Language Model) to transform raw content into well-structured transcripts
- Optimize text for audio narration

### 3. Audio Generation (`audio_maker`)
- Convert generated transcripts into spoken audio
- Use text-to-speech models to create natural-sounding narration
- Output audio files in desired formats

## Setup

1. Create a Notion integration and get your API key:
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Give it a name and submit
   - Copy the API key

2. Share your database with the integration:
   - Open your Notion database
   - Click "Share" in the top right
   - Click "Add people, emails, groups, or integrations"
   - Search for your integration name and select it

3. Get your database ID:
   - Open your database in Notion
   - Copy the database ID from the URL:
     - The URL format is: https://www.notion.so/{workspace}/{database_id}?v={view_id}
     - The database ID is a 32-character string

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file with your credentials:
```
NOTION_API_KEY=your_api_key_here
NOTION_DATABASE_ID=your_database_id_here
LLM_API_KEY=your_llm_api_key_here
```

## Usage

### Notion to PDF Export
```bash
python -m notion_extract.notion_to_pdf
```

### Notion to Text Export
```bash
python -m notion_extract.notion_to_text
```

### Generate Transcripts from Text
```bash
python -m transcript_maker.generate_transcript --input path/to/text_files --output path/to/transcripts
```

### Create Audio from Transcripts
```bash
python -m audio_maker.text_to_speech --input path/to/transcripts --output path/to/audio_files
```

## Complete Workflow

You can run the entire pipeline with:
```bash
python -m main
```

This will:
1. Extract content from your Notion database
2. Process the raw text into well-structured transcripts
3. Generate audio files from those transcripts

## Technical Overview

### Notion Extraction
- Uses Notion's official API to retrieve database pages
- Can export to both PDF and plain text formats
- Handles pagination and API rate limiting

### Transcript Processing  
- Processes raw text through an LLM to create natural-sounding transcripts
- Applies formatting and structure optimization for better speech synthesis
- Breaks content into appropriate segments for audio generation

### Audio Generation
- Converts processed transcripts into natural-sounding audio
- Supports various text-to-speech models
- Allows configuration of voice, speed, and other audio parameters

## Project Structure
The project is organized into the following packages:
- `notion_extract`: Content extraction from Notion
  - `dto`: Data transfer objects for Notion API
  - `helper`: Helper services for Notion operations
  - `notion_to_pdf.py`: PDF export functionality
  - `notion_to_text.py`: Text export functionality
- `transcript_maker`: Transcript generation from raw text
  - `llm_processor.py`: LLM integration for content processing
  - `generate_transcript.py`: Main transcript generation script
- `audio_maker`: Audio generation from transcripts
  - `text_to_speech.py`: Text-to-speech conversion
  - `audio_processor.py`: Audio file processing utilities

## Requirements
- Python 3.8+
- Notion API access
- Access to an LLM API (like OpenAI GPT)
- Text-to-speech service access

## License
[Specify your license here]
