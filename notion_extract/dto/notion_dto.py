from dataclasses import dataclass
from typing import List

@dataclass
class NotionBlock:
    type: str
    content: str
    indent_level: int
    has_children: bool

@dataclass
class NotionPage:
    id: str
    title: str
    blocks: List[NotionBlock]