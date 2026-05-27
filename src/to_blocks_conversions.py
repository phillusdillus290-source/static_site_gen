from enum import Enum

from htmlnode import ParentNode
from to_markdown_conversions import text_to_textnodes
from textnode import text_node_to_html_node, TextNode, TextType

def markdown_to_blocks(markdown):
    return markdown.strip().split("\n\n")

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def _headcheck(markdown_block):
    if markdown_block.startswith("#"):
        return 1 + _headcheck(markdown_block[1::])
    return 0

def block_to_block_type(markdown_block):
    heading_count = _headcheck(markdown_block)
    if heading_count - 1 in range(6) and len(markdown_block) > heading_count:
        if markdown_block[heading_count] == " ":
            return BlockType.HEADING
    if markdown_block.startswith("```\n") and markdown_block.endswith("```"):
        return BlockType.CODE
    markdown_lines = markdown_block.split("\n")
    quote_count = 0
    unordered_list_count = 0
    ordered_list_count = 1
    for line in markdown_lines:
        if line.startswith(">"):
            quote_count += 1
        if line.startswith("- "):
            unordered_list_count += 1
        if line.startswith(f"{ordered_list_count}. "):
            ordered_list_count += 1
    if quote_count == len(markdown_lines):
        return BlockType.QUOTE
    if unordered_list_count == len(markdown_lines):
        return BlockType.UNORDERED_LIST
    if ordered_list_count - 1 == len(markdown_lines):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def text_to_children(text):
    textnodes = text_to_textnodes(text)
    children = []
    for node in textnodes:
        children.append(text_node_to_html_node(node))
    return children

def paragraph_to_htmlnode(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    return ParentNode("p", text_to_children(paragraph))

def heading_to_htmlnode(block):
    degree = 0
    for char in block:
        if char == "#":
            degree += 1
        else:
            break
    text = block[degree + 1:]
    return ParentNode(f"h{degree}", text_to_children(text))

def code_to_htmlnode(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("invalid code block")
    text =  block[4:-3]
    raw_text_node = TextNode(text, TextType.TEXT)
    child = text_node_to_html_node(raw_text_node)
    code = ParentNode("code", [child])
    return ParentNode("pre", [code])

def quote_to_htmlnode(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)

def ulist_to_htmlnode(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)

def olist_to_htmlnode(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        parts = item.split(". ", 1)
        text = parts[1]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)

def block_to_htmlnode(block):
    blocktype = block_to_block_type(block)
    if blocktype == BlockType.PARAGRAPH:
        return paragraph_to_htmlnode(block)
    if blocktype == BlockType.HEADING:
        return heading_to_htmlnode(block)
    if blocktype == BlockType.CODE:
        return code_to_htmlnode(block)
    if blocktype == BlockType.QUOTE:
        return quote_to_htmlnode(block)
    if blocktype == BlockType.UNORDERED_LIST:
        return ulist_to_htmlnode(block)
    if blocktype == BlockType.ORDERED_LIST:
        return olist_to_htmlnode(block)
    raise ValueError("invalid block type")

def markdown_to_htmlnode(markdown):
    children = []
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        html_node = block_to_htmlnode(block)
        children.append(html_node)
    return ParentNode("div", children, None)
        