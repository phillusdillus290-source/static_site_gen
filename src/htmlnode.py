class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError("feature not implemented")
    
    def props_to_html(self):
        string = ""
        if self.props:
            prop_keys = list(self.props.keys())
            for key in prop_keys:
                string += f" {key}=\"{self.props[key]}\""
        return string

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
    

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)
    
    def to_html(self):
        if self.value == None:
            raise ValueError("no value given")
        if self.tag == None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
    
    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.props})"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)
    
    def to_html(self):
        if not self.tag:
            raise ValueError("no tag given")
        if self.children == None:
            raise ValueError("no children listed")
        string = f"<{self.tag}>"
        for child in self.children:
            string += child.to_html()
        return string + f"</{self.tag}>"