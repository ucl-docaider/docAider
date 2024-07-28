import os
import markdown

# Define the extensions for HTML and Markdown files
HTML_EXTENSION = '.html'
MD_EXTENSION = '.md'

# Load HTML template parts
with open('/repo-copilot/repo_documentation/merging/head.html', 'r', encoding='utf-8') as f:
    head = f.read()

with open('/repo-copilot/repo_documentation/merging/body.html', 'r', encoding='utf-8') as f:
    body = f.read()

with open('/repo-copilot/repo_documentation/merging/file-card.html', 'r', encoding='utf-8') as f:
    file_card_template = f.read()

with open('/repo-copilot/repo_documentation/merging/script.html', 'r', encoding='utf-8') as f:
    script = f.read()

def create_documentation(docs_folder):
    # Generate table of contents
    files = []
    for root, _, _files in os.walk(docs_folder):
        for file in _files:
            if file.endswith(MD_EXTENSION) and not file.startswith('index'):
                path = os.path.relpath(os.path.join(root, file), docs_folder)
                print(path)
                files.append((root, path))

    # Sort by basename
    files.sort(key=lambda x: os.path.basename(x[1]))

    # Get table of contents
    tree = to_tree([path for _, path in files])
    print(f"Tree: {tree}")
    print(f"Files: {files}")
    table_of_contents = get_table_of_contents(tree)

    # Get the documentation file-cards
    documentation_content = get_documentation_content(files)

    # Replace placeholders in the template
    filled_template = body.format(
        table_of_contents=table_of_contents,
        documentation_content=documentation_content,
        script=script
    )

    # Write the filled template to the output file
    output = head + filled_template
    output_file = os.path.join(docs_folder, f'index{HTML_EXTENSION}')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Final documentation has been generated in {output_file}")

def create_file_card(file_path: str, docs):
    # Clean the path to create a valid HTML id
    id = clean_path(file_path)
    # Remove file extensions for display purposes
    file_name = file_path.replace('\\', '/').replace(MD_EXTENSION, '')
    # Format the file card template with the id and content
    return file_card_template.format(id=id, file_name=file_name, content=docs)

def get_table_of_contents(tree, prefix=""):
    table_of_contents = "<ul>\n"

    # Separate directories and files
    directories = []
    files = []
    for key, value in tree.items():
        if key == 'files':
            files.extend(value)
        elif isinstance(value, dict):
            directories.append((key, value))
        else:
            files.append(key)

    # Sort directories alphabetically
    directories.sort(key=lambda x: x[0].lower())

    # Sort files alphabetically
    files.sort(key=str.lower)

    # Handle directories first
    for key, value in directories:
        table_of_contents += f'<li><details><summary>📁 {key}</summary>\n'
        table_of_contents += get_table_of_contents(value, prefix + key + "/")
        table_of_contents += '</details></li>\n'

    # Then handle files
    for file in files:
        id = clean_path(prefix + file)
        link = os.path.basename(file).replace(MD_EXTENSION, '')
        table_of_contents += f'<li><a href="javascript:void(0);" onclick="showFile(\'{id}\')">🐍 {link}</a></li>\n'

    table_of_contents += "</ul>\n"
    return table_of_contents

def clean_path(path):
    # Clean the path to create a valid HTML id
    return path.replace(MD_EXTENSION, '') \
        .replace('\\', '/') \
        .replace('/', '-') \
        .replace('.', '-')

def get_documentation_content(files):
    documentation_content = ""
    for root, path in files:
        basename = os.path.basename(path)
        file_path = os.path.join(root, basename)
        with open(file_path, 'r', encoding='utf-8') as f:
            # Convert Markdown files to HTML
            content = markdown.markdown(f.read(), extensions=['fenced_code'])
            # Create file card for each file
            documentation_content += create_file_card(path, content)
    return documentation_content

def to_tree(files):
    tree = {'files': []}
    for path in files:
        parts = path.split(os.sep)
        current = tree
        for part in parts[:-1]:
            if part not in current:
                current[part] = {'files': []}
            current = current[part]
        if parts[-1]:
            current['files'].append(parts[-1])
    return tree