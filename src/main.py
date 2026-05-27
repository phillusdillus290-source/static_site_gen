import os, shutil

from webpage_gen import generate_pages_recursive

from textnode import TextNode, TextType

def copier(base="./static", target="./public"):
    if os.path.exists(target):
        shutil.rmtree(target)
    os.mkdir(target)
    surface = os.listdir(base)
    for item in surface:
        item_path = os.path.join(base, item)
        if os.path.isfile(item_path):
            shutil.copy(item_path, target)
        else:
            copier(item_path, os.path.join(target, item))

def main():
    copier()
    generate_pages_recursive("./content", "./template.html", "./public")

main()