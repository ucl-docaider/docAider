import os
from datetime import datetime

EXTENSION = '.html'

with open('repo_documentation/merging/head.html', 'r', encoding='utf-8') as f:
    head = f.read()

with open('repo_documentation/merging/body.html', 'r', encoding='utf-8') as f:
    body = f.read()

with open('repo_documentation/merging/file-card.html', 'r', encoding='utf-8') as f:
    file_card_template = f.read()

with open('repo_documentation/merging/script.html', 'r', encoding='utf-8') as f:
    script = f.read()


class TemplateDto:
    def __init__(self, project_title, repo_url, project_description, report_bug_url, feature_request_url):
        self.project_title = project_title
        self.repo_url = repo_url
        self.project_description = project_description
        self.report_bug_url = report_bug_url
        self.feature_request_url = feature_request_url


def create_documentation(docs_folder, dto: TemplateDto):
    # Get the current date and time
    current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Generate table of contents
    files = []
    for root, _, _files in os.walk(docs_folder):
        for file in _files:
            if file.endswith(EXTENSION) and not file.startswith('index'):
                path = os.path.relpath(os.path.join(root, file), docs_folder)
                files.append((root, path))

    # Sort by basename
    files.sort(key=lambda x: os.path.basename(x[1]))

    # Get table of contents
    tree = to_tree([path for _, path in files])
    table_of_contents = get_table_of_contents(tree)

    # Get the documentation file-cards
    documentation_content = get_documentation_content(files)

    # Replace placeholders in the template
    filled_template = body.format(
        project_title=dto.project_title,
        repo_url=dto.repo_url,
        project_description=dto.project_description,
        report_bug_url=dto.report_bug_url,
        feature_request_url=dto.feature_request_url,
        table_of_contents=table_of_contents,
        documentation_content=documentation_content,
        generation_date=current_datetime,
        script=script
    )

    # Write the filled template to the output file
    output = head + filled_template
    output_file = os.path.join(docs_folder, f'index{EXTENSION}')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Final documentation has been generated in {output_file}")


def create_file_card(file_path: str, docs):
    id = clean_path(file_path)
    file_name = file_path.replace('\\', '/').replace('.html', '')
    return file_card_template.format(id=id,
                                     file_name=file_name,
                                     content=docs)


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
        link = os.path.basename(file).replace(EXTENSION, '')
        table_of_contents += f'<li><a href="javascript:void(0);" onclick="showFile(\'{id}\')">🐍 {link}</a></li>\n'


    table_of_contents += "</ul>\n"
    return table_of_contents


def clean_path(path):
    return path.replace(EXTENSION, '') \
        .replace('\\', '/') \
        .replace('/', '-') \
        .replace('.', '-')


def get_documentation_content(files):
    documentation_content = ""
    for root, path in files:
        basename = os.path.basename(path)
        with open(os.path.join(root, basename), 'r', encoding='utf-8') as f:
            documentation_content += create_file_card(path, f.read())
    return documentation_content


def to_tree(files):
    tree = {}
    for path in files:
        parts = path.split('\\')
        current = tree
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        if isinstance(current, dict):
            if 'files' not in current:
                current['files'] = []
            current['files'].append(parts[-1])
        else:
            current.append(parts[-1])
    return tree


"""
TODO
- Add a search bar (file_name)
- Add created with 'Repo-Copilot' in the footer (link to repo)

Hard TODO
- Add dark and light mode
- Folow the tree structure of the files (folder/file)
"""
