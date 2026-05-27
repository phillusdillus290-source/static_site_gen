import os, shutil

from to_blocks_conversions import markdown_to_htmlnode

from main import basepath

def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line
    raise Exception("no header")
    
def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    from_file = open(from_path)
    template_file = open(template_path)
    dest_file = open(dest_path, mode="x+")
    from_content = from_file.read()
    template_content = template_file.read()
    from_html = markdown_to_htmlnode(from_content).to_html()
    title = extract_title(from_content)
    new_content = template_content.replace("{{ Title }}", title).replace("{{ Content }}", from_html).replace("href=\"/", f"href=\"{basepath}").replace("src=\"/", f"src=\"{basepath}")
    dest_file.write(new_content)
    from_file.close()
    template_file.close()
    dest_file.close()

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    content = os.listdir(dir_path_content)
    for branch in content:
        branch_path = os.path.join(dir_path_content, branch)
        dest_path = os.path.join(dest_dir_path, branch)
        if os.path.isfile(branch_path) and branch.endswith(".md"):
            generate_page(branch_path, template_path, dest_path[:-3] + ".html")
        else:
            os.mkdir(dest_path)
            generate_pages_recursive(branch_path, template_path, dest_path)