from textnode import TextType, TextNode

import re

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        text_chunks = node.text.split(delimiter)
        if len(text_chunks) % 2 == 0:
            raise Exception("closing delimiter not found")
        for i in range(len(text_chunks)):
            if i % 2 != 0:
                new_nodes.append(TextNode(text_chunks[i], text_type))
            else:
                new_nodes.append(TextNode(text_chunks[i], TextType.TEXT))
    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if not node.text:
            continue
        image_extractions = extract_markdown_images(node.text)
        if not image_extractions:
            new_nodes.append(node)
            continue
        text_chunks = node.text
        for image in image_extractions:
            text_chunks = text_chunks.split(f"![{image[0]}]({image[1]})", 1)
            if text_chunks[0]:
                new_nodes.append(TextNode(text_chunks[0], TextType.TEXT))
            new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            text_chunks = text_chunks[1]
        if text_chunks:
            new_nodes.append(TextNode(text_chunks, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if not node.text:
            continue
        link_extractions = extract_markdown_links(node.text)
        if not link_extractions:
            new_nodes.append(node)
            continue
        text_chunks = node.text
        for link in link_extractions:
            text_chunks = text_chunks.split(f"[{link[0]}]({link[1]})", 1)
            if text_chunks[0]:
                new_nodes.append(TextNode(text_chunks[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            text_chunks = text_chunks[1]
        if text_chunks:
            new_nodes.append(TextNode(text_chunks, TextType.TEXT))
    return new_nodes

def assist_to_delim_textnodes(node_list, delimiter, texttype):
    new_list = []
    for node in node_list:
        if node.text_type == TextType.TEXT:
            special = split_nodes_delimiter([node], delimiter, texttype)
            for spec_node in special:
                new_list.append(spec_node)
        else:
            new_list.append(node)
    return new_list

def assist_to_extras_textnodes(node_list, function):
    new_list = []
    for node in node_list:
        if node.text_type == TextType.TEXT:
            images = function([node])
            for i_node in images:
                new_list.append(i_node)
        else:
            new_list.append(node)
    return new_list

def text_to_textnodes(text):
    textnode = TextNode(text, TextType.TEXT)
    with_bold = assist_to_delim_textnodes([textnode], "**", TextType.BOLD)
    with_italic = assist_to_delim_textnodes(with_bold, "_", TextType.ITALIC)
    with_code = assist_to_delim_textnodes(with_italic, "`", TextType.CODE)
    with_images = assist_to_extras_textnodes(with_code, split_nodes_image)
    with_links = assist_to_extras_textnodes(with_images, split_nodes_link)
    final = with_links
    return final