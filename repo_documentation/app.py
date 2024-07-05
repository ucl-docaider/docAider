import utils
import os
import sys
import time
from prompt import DOCUMENTATION_PROMPT

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from autogen_utils import utils as autogen_utils
from cache.docs_cache import DocsCache
from code2flow.code2flow import utils as graph_utils

class RepoDocumentation():
    def __init__(self, root_folder):
        self.root_folder = os.path.abspath(root_folder)
        self.output_dir = os.path.join(self.root_folder, "docs_output")
        self.assistant = autogen_utils.load_assistant_agent()
        self.user = autogen_utils.load_user_agent()

    def run(self):
        print('Generating documentation...')
        print(f'Root folder: {self.root_folder}')
        print(f'Output folder: {self.output_dir}')
        start_time = time.time()

        # 1. Generate graph
        graph_utils.generate_graph(self.root_folder, self.output_dir)
        graph = graph_utils.get_call_graph(self.output_dir)

        # 2. Build mapping of a file to the functions called within them
        file_to_calls = graph_utils.get_file_to_functions(graph)

        # 3. Build BFS exploration of the call graph
        bfs_explore = graph_utils.explore_call_graph(graph)

        # 4. Prepare cache, where we will map file paths to their respective documentation
        cache = DocsCache()

        # 5. Generate documentation for each file and function within
        for file_path, calls in file_to_calls.items():
            if file_path == 'EXTERNAL':  # Skip all external functions
                continue

            print(f"Generating documentation for file={file_path}")
            additional_docs = self._get_additional_docs(
                calls, graph, bfs_explore)
            file_content = utils.read_file_content(file_path)
            docs = self._generate_file_docs(
                file_path, file_content, additional_docs)
            docs_filepath = self._write_file_docs(file_path, docs)

            # 6. Add the file path and its according documentation to the cache
            cache.add(file_path, docs_filepath)

        # 7. Save cache to a file
        graph_utils.write_json(
            f'{self.output_dir}/cache.json', cache.to_dict())

        total = round(time.time() - start_time, 3)
        print(f'Generated documentation ({
              cache.size()} files) can be found in {self.output_dir}')
        print(f"Documentation generation completed in {total}s.")

    def _get_additional_docs(self, calls, graph, bfs_explore):
        additional_docs = ""
        for call_name in calls:
            call = graph[call_name]
            if 'EXTERNAL' in call['file_name']:
                continue
            for callee in bfs_explore[call_name]:
                callee_call = graph[callee]
                additional_docs += f"\nFunction/Class {
                    callee_call['name']}:\n{callee_call['content']}\n"
        return additional_docs

    def _generate_file_docs(self, file_path, file_content, additional_docs):
        prompt_message = DOCUMENTATION_PROMPT.format(
            file_name=os.path.basename(file_path),
            file_content=file_content,
            root_folder=self.root_folder,
            additional_docs=additional_docs
        )
        autogen_utils.initiate_chat(self.user, self.assistant, prompt_message)
        utils.save_prompt_debug(
            self.output_dir, os.path.basename(file_path), prompt_message)
        return self.assistant.last_message()['content']

    def _write_file_docs(self, file_path, docs) -> str:
        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Get the path that relative from root folder
        rel_path = os.path.relpath(file_path, self.root_folder)

        # Write the docs to a markdown file
        rel_path += '.md'
        output_file_path = os.path.join(self.output_dir, rel_path)
        with open(output_file_path, 'w') as file:
            file.write(docs)
        return output_file_path


RepoDocumentation(root_folder='../simple-users/').run()
