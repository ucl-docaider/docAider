import os
from datetime import datetime

EXTENSION = '.html'


class TemplateDto:
    def __init__(self, project_title, repo_url, project_description, report_bug_url, feature_request_url):
        self.project_title = project_title
        self.repo_url = repo_url
        self.project_description = project_description
        self.report_bug_url = report_bug_url
        self.feature_request_url = feature_request_url


def create_documentation(docs_folder, dto: TemplateDto):
    head_path = 'repo_documentation/merging/head.html'
    body_path = 'repo_documentation/merging/body.html'

    # Get the current date and time
    current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Read the body
    with open(head_path, 'r', encoding='utf-8') as f:
        head = f.read()
    with open(body_path, 'r', encoding='utf-8') as f:
        body = f.read()

    # Generate table of contents
    table_of_contents = ""
    for root, _, files in os.walk(docs_folder):
        for file in files:
            if file.endswith(EXTENSION) and not file.startswith('index'):
                rel_path = os.path.relpath(
                    os.path.join(root, file), docs_folder)
                link = rel_path.replace('\\', '/').replace(EXTENSION, '')
                id = link.replace('/', '-').replace('.', '-')
                table_of_contents += f'<li><a href="#{id}">{link}</a></li>\n'

    # Generate documentation content
    documentation_content = ""
    for root, _, files in os.walk(docs_folder):
        for file in files:
            if file.endswith(EXTENSION) and not file.startswith('index'):
                rel_path = os.path.relpath(
                    os.path.join(root, file), docs_folder)
                link = rel_path.replace('\\', '/').replace(EXTENSION, '')
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    documentation_content += create_file_card(link, f.read())

      # Replace placeholders in the template
    script = get_script()
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
    id = file_path.replace('/', '-').replace('.', '-')
    return f"""
<div class="file-card">
    <details>
        <summary id="{id}">{file_path}</summary>
        <div class="content">
            {docs}
        </div>
    </details>
</div>
"""


def get_script():
    return """
<script>
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
</script>
"""


"""
TODO
- Remove the files section (table of contents) add it as a sidebar, so it's easier to navigate
- Add fold all and unfold all buttons that scrolls with the page
- Add a 'Scroll to top' button that scrolls with the page
- Add a search bar (file_name)
- Add created with 'Repo-Copilot' in the footer (link to repo)

Hard TODO
- Add dark and light mode
- Add a button to copy the documentation to the clipboard
- Add a button to download the documentation as a PDF
- Folow the tree structure of the files (folder/file)
- 

"""