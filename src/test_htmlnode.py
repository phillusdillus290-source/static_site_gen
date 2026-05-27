import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

from textnode import TextNode, TextType, text_node_to_html_node

from to_markdown_conversions import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes

from to_blocks_conversions import markdown_to_blocks, block_to_block_type, markdown_to_htmlnode, text_to_children, BlockType

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode("a", "click me", None, {"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')

    def test_props_to_html_eq(self):
        node1 = HTMLNode("a", "click me", None, {"href": "https://www.google.com", "target": "_blank"})
        node2 = HTMLNode("a", "click me", None, {"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node1.props_to_html(), node2.props_to_html())

    def test_props_to_html_xeq(self):
        node1 = HTMLNode("a", "click me", None, {"href": "https://www.google.com", "target": "_blank"})
        node2 = HTMLNode("a", "click me", None, {"href": "https://www.boot.dev", "target": "_blank"})
        self.assertNotEqual(node1.props_to_html(), node2.props_to_html())

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Hello, world!")
        self.assertEqual(node.to_html(), "<a>Hello, world!</a>")

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_empty_children(self):
        node = ParentNode("div", [])
        self.assertEqual(node.to_html(), "<div></div>")

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a text node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a text node")

    def test_italic(self):
        node = TextNode("This is a text node", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is a text node")

    def test_code(self):
        node = TextNode("This is a text node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a text node")

    def test_link(self):
        node = TextNode("This is a text node", TextType.LINK)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is a text node")
        self.assertEqual(html_node.props, {"href": None})

    def test_image(self):
        node = TextNode("This is a text node", TextType.IMAGE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": None, "alt": "This is a text node"})

    def test_bold_conversion_middle(self):
        node = TextNode("This has a **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(new_nodes, [TextNode("This has a ", TextType.TEXT), TextNode("bold", TextType.BOLD), TextNode(" word", TextType.TEXT)])

    def test_bold_conversion_first(self):
        node = TextNode("**This** has a bold word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(new_nodes, [TextNode("", TextType.TEXT), TextNode("This", TextType.BOLD), TextNode(" has a bold word", TextType.TEXT)])

    def test_bold_conversion_end(self):
        node = TextNode("This has a bold **word**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(new_nodes, [TextNode("This has a bold ", TextType.TEXT), TextNode("word", TextType.BOLD), TextNode("", TextType.TEXT)])

    def test_italic_conversion_middle(self):
        node = TextNode("This has an _italic_ word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertListEqual(new_nodes, [TextNode("This has an ", TextType.TEXT), TextNode("italic", TextType.ITALIC), TextNode(" word", TextType.TEXT)])

    def test_no_delimiter(self):
        node = TextNode("This is a node", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(new_nodes, [node])

    def test_conversion_middle_many(self):
        node1 = TextNode("This has a **bold** word", TextType.TEXT)
        node2 = TextNode("This has a **bold** word too", TextType.TEXT)
        node3 = TextNode("This also has a **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node1, node2, node3], "**", TextType.BOLD)
        self.assertListEqual(new_nodes, [TextNode("This has a ", TextType.TEXT), TextNode("bold", TextType.BOLD), TextNode(" word", TextType.TEXT), TextNode("This has a ", TextType.TEXT), TextNode("bold", TextType.BOLD), TextNode(" word too", TextType.TEXT), TextNode("This also has a ", TextType.TEXT), TextNode("bold", TextType.BOLD), TextNode(" word", TextType.TEXT)])

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link to boot dev](https://www.boot.dev)"
        )
        self.assertListEqual([("link to boot dev", "https://www.boot.dev")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link to [boot dev](https://boot.dev) and another link to [google](https://google.com)",
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link to ", TextType.TEXT),
                TextNode("boot dev", TextType.LINK, "https://boot.dev"),
                TextNode(" and another link to ", TextType.TEXT),
                TextNode("google", TextType.LINK, "https://google.com"),
            ],
            new_nodes,
        )

    def test_split_images_lone(self):
        node = TextNode("![Lonely GOpher](https://i.imgur.com/3elNhQu.png)", TextType.TEXT)
        new_node = split_nodes_image([node])
        self.assertListEqual([TextNode("Lonely GOpher", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png")], new_node)

    def test_split_links_lone(self):
        node = TextNode("[Lonely link](https://boot.dev)", TextType.TEXT)
        new_node = split_nodes_link([node])
        self.assertListEqual([TextNode("Lonely link", TextType.LINK, "https://boot.dev")], new_node)

    def test_consecutive_images(self):
        node = TextNode(
            "This is text with two images: ![image](https://i.imgur.com/zjjcJKZ.png)![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with two images: ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_consecutive_links(self):
        node = TextNode(
            "This is text with two links: [link](https://boot.dev)[second link](https://google.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with two links: ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(
                    "second link", TextType.LINK, "https://google.com"
                ),
            ],
            new_nodes,
        )

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type_paragraph(self):
        md = """
This is a one-sentence paragraph
"""
        blocktype = block_to_block_type(md)
        self.assertEqual(blocktype, BlockType.PARAGRAPH)

    def test_block_to_block_type_headings(self):
        md = """
# This is a one-hastag heading

### This is a three-hastag heading

This is not a heading

#this_aint_a_heading
"""
        blocktype_list = []
        blocks = markdown_to_blocks(md)
        for block in blocks:
            blocktype_list.append(block_to_block_type(block))
        self.assertEqual(
            blocktype_list,
            [
                BlockType.HEADING,
                BlockType.HEADING,
                BlockType.PARAGRAPH,
                BlockType.PARAGRAPH
            ]
        )

    def test_block_to_block_code(self):
        md = """
```
This is code
```

```
This is also code```

```This isn't code```
"""
        blocktype_list = []
        blocks = markdown_to_blocks(md)
        for block in blocks:
            blocktype_list.append(block_to_block_type(block))
        self.assertEqual(
            blocktype_list,
            [
                BlockType.CODE,
                BlockType.CODE,
                BlockType.PARAGRAPH
            ]
        )

    def test_block_to_block_quote(self):
        md = """
>\"This is a quote\"

> \"This is also a quote

> \"This is
> \"a quote
>\"block

>this is a quote

>"this isn't
a quote
"""
        blocktype_list = []
        blocks = markdown_to_blocks(md)
        for block in blocks:
            blocktype_list.append(block_to_block_type(block))
        self.assertEqual(
            blocktype_list,
            [
                BlockType.QUOTE,
                BlockType.QUOTE,
                BlockType.QUOTE,
                BlockType.QUOTE,
                BlockType.PARAGRAPH
            ]
        )

    def test_block_to_block_unordered_list(self):
        md = """
- This is a list

- This is
- also a list

-this isn't a list

-This isn't
a list either
"""
        blocktype_list = []
        blocks = markdown_to_blocks(md)
        for block in blocks:
            blocktype_list.append(block_to_block_type(block))
        self.assertEqual(
            blocktype_list,
            [
                BlockType.UNORDERED_LIST,
                BlockType.UNORDERED_LIST,
                BlockType.PARAGRAPH,
                BlockType.PARAGRAPH
            ]
        )

    def test_block_to_block_ordered_list(self):
        md = """
1. This is a list

1. This is
2. also a list

1.thisaintalsit

1. this isn't
a list either

2. wrong starting number, biatch
"""
        blocktype_list = []
        blocks = markdown_to_blocks(md)
        for block in blocks:
            blocktype_list.append(block_to_block_type(block))
        self.assertEqual(
            blocktype_list,
            [
                BlockType.ORDERED_LIST,
                BlockType.ORDERED_LIST,
                BlockType.PARAGRAPH,
                BlockType.PARAGRAPH,
                BlockType.PARAGRAPH
            ]
        )

    def test_paragraph_to_htmlnode(self):
        md = "This is a one-sentence paragraph"
        node = markdown_to_htmlnode(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is a one-sentence paragraph</p></div>"
        )

    def test_multiple_paragraph_to_htmlnode(self):
        md = """This is a one-sentence paragraph

This is another one-sentence paragraph"""
        node = markdown_to_htmlnode(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is a one-sentence paragraph</p><p>This is another one-sentence paragraph</p></div>"
        )