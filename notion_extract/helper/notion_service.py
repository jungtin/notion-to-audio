import os
from dotenv import load_dotenv
from notion_client import Client
from typing import Dict, Any, List
from notion_extract.dto.notion_dto import NotionBlock, NotionPage

def init_notion_client() -> Client:
    """Initialize and return the Notion client."""
    load_dotenv()
    notion_api_key = os.getenv("NOTION_API_KEY")
    
    if not notion_api_key:
        raise ValueError("NOTION_API_KEY not found in environment variables")
    
    return Client(auth=notion_api_key)

def get_database_pages(notion: Client, database_id: str) -> list[Dict[str, Any]]:
    """Retrieve all pages from the specified database, sorted by their order."""
    try:
        # Query the database with sorting
        response = notion.databases.query(
            database_id=database_id,
            sorts=[{
                "timestamp": "created_time",
                "direction": "ascending"
            }]
        )
        return response.get("results", [])
    except Exception as e:
        print(f"Error querying database: {e}")
        return []

def extract_block_content(block: Dict[str, Any]) -> str:
    """Extract content from a block based on its type."""
    block_type = block.get("type", "")
    if not block_type in block:
        return ""

    block_data = block[block_type]

    # Handle different block types
    if "rich_text" in block_data:
        text_content = [text.get("plain_text", "") for text in block_data["rich_text"]]
        return " ".join(text_content)
    elif "text" in block_data:
        text_content = [text.get("plain_text", "") for text in block_data["text"]]
        return " ".join(text_content)
    elif block_type == "child_page":
        return block_data.get("title", "")
    
    return ""

def extract_blocks(notion: Client, page_id: str, indent: int = 0) -> List[NotionBlock]:
    """Recursively extract blocks and their children."""
    result_blocks = []
    api_blocks = notion.blocks.children.list(block_id=page_id).get("results", [])
    
    for block in api_blocks:
        block_type = block.get("type", "")
        content = extract_block_content(block)
        has_children = block.get("has_children", False)
        
        if content:
            result_blocks.append(NotionBlock(
                type=block_type,
                content=content,
                indent_level=indent,
                has_children=has_children
            ))
        
        if has_children:
            # child_indent = indent + 1 if block_type == "toggle" else indent
            child_indent = indent + 1
            result_blocks.extend(extract_blocks(notion, block["id"], child_indent))
    
    return result_blocks

def extract_page_content(notion: Client, page: Dict[str, Any]) -> NotionPage:
    """Extract all content from a page and return structured data."""
    try:
        page_id = page["id"]
        page_title = page.get("properties", {}).get("Name", {}).get("title", [{}])[0].get("plain_text", "Untitled")
        blocks = extract_blocks(notion, page_id)
        
        return NotionPage(
            id=page_id,
            title=page_title,
            blocks=blocks
        )
    
    except Exception as e:
        print(f"Error processing page: {e}")
        # return NotionPage(id="", title="Error", blocks=[])
        return None

def print_page(page: NotionPage) -> None:
    """Print the page content in a formatted way."""
    print(f"\n{'='*50}")
    print(f"Page: {page.title}")
    print(f"ID: {page.id}\n")
    
    for block in page.blocks:
        indent_str = "  - " * block.indent_level
        print(f"{indent_str}{block.type.capitalize()}: {block.content}")