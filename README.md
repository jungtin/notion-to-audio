# Notion Database to PDF Exporter

This script allows you to export all pages from a Notion database to PDF format and merge them into a single PDF file. It uses Notion's official API to handle the exports. The project is organized into packages for better code structure.

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
```

## Usage

Run the script:
```bash
python -m notion_extract.notion_to_pdf
```

The script will:
1. Connect to your Notion database to get all pages
2. Export each page to PDF format using Notion's API
3. Merge all PDFs into a single file named `merged_output.pdf`
4. Clean up individual PDF files

## How it Works

This script uses:
- The Notion API to retrieve database pages and export them to PDF
- PyPDF2 to merge the individual PDFs into a single file

## Note
Make sure your Notion integration has access to the database and all its pages before running the script.

## Project Structure
The project is organized into the following packages:
- `notion_extract`: Contains the main scripts for exporting Notion databases to PDFs and text
  - `dto`: Data transfer objects for Notion API
  - `helper`: Helper services for Notion operations
- `audio_maker`: Scripts for generating audio from text
- `transcript_maker`: Scripts for generating transcripts
