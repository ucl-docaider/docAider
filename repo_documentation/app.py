import utils
import os
import sys
import time

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from code2flow.code2flow import utils as graph_utils
from cache.docs_cache import DocsCache
from autogen_utils import utils as autogen_utils

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

            additional_docs = autogen_utils.get_additional_docs_calls(
                calls, graph, bfs_explore)
            file_content = utils.read_file_content(file_path)

            # Generate documentation for the file
            docs = autogen_utils.get_documentation(
                file_path=file_path,
                file_content=file_content,
                additional_docs=additional_docs,
                user=self.user,
                assistant=self.assistant,
                output_dir=self.output_dir,
                root_folder=self.root_folder,
                save_debug=True
            )

            # Write the documentation to a file
            docs_filepath = utils.write_file_docs(output_dir=self.output_dir,
                                                  root_folder=self.root_folder,
                                                  file_path=file_path,
                                                  docs=docs)

            # 6. Add the file path and its according documentation to the cache
            cache.add(file_path, docs_filepath)

        # 7. Save cache to a file
        utils.save_cache(self.output_dir, cache)

        total = round(time.time() - start_time, 3)
        print(f'Generated documentation ({cache.size()} files) can be found in {self.output_dir}')
        print(f"Documentation generation completed in {total}s.")


RepoDocumentation(root_folder='../code2flow/projects/simple').run()
