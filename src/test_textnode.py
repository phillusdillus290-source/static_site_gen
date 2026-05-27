import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node1 = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a different text node", TextType.BOLD)
        self.assertNotEqual(node1, node2)

    def test_empty_link(self):
        node = TextNode("This is a text node", TextType.LINK)
        self.assertEqual(node.url, None)

    def test_bootdev_link(self):
        node = TextNode("boot.dev", TextType.LINK, "https://www.boot.dev")
        self.assertEqual(node.url, "https://www.boot.dev")

    def test_text_type_not_eq1(self):
        node1 = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node1, node2)
        
    def test_text_type_not_eq2(self):
        node1 = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is also a text node", TextType.ITALIC)
        self.assertNotEqual(node1, node2)
        


if __name__ == "__main__":
    unittest.main()