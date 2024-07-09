import os, sys, time, asyncio, utils
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from dotenv import load_dotenv
from rag.generator import DocumentationGenerator
from repo_utils.saver import RepoSaver
from code2flow.code2flow import utils as graph_utils
from cache.docs_cache import DocsCache
from autogen_utils import utils as autogen_utils

load_dotenv(dotenv_path='.env')

class RepoDocumentation():
    """
    This class provides a set of functions to generate documentation for a repository
    """
    def __init__(self, llm_id, root_folder, output_dir):
        """
        Initializes a new instance of the RepoDocumentation class.
        
        Args:
            llm_id: Ollama model name, see https://ollama.ai/library
            root_folder: we generate documentation for all source files under the root folder.
            output_dir: the directory stores the output files and documentation
            documentation_generator: the instance of documentation generator class
        """
        self.llm_id = llm_id
        self.root_folder = root_folder
        self.output_dir = os.path.join(self.root_folder, output_dir)
        self.documentation_generator = DocumentationGenerator(llm_id)
        
        repo_saver = RepoSaver("CQ-Ke/repo-copilot-test")
        repo_saver.auto_save_python_and_md_files()

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

            additional_docs = autogen_utils.get_additional_docs_calls(calls, graph, bfs_explore)
            source_code = asyncio.run(
                self.documentation_generator.context_retriever.search(query=f"{file_path}")
            )
            documentation = asyncio.run(self.documentation_generator.generate_documentation(
                file_path=file_path,
                file_content=source_code,
                root_folder=self.root_folder,
                additional_docs=additional_docs
            ))
            # Write the documentation to a file
            docs_filepath = utils.write_file_docs(
                output_dir=self.output_dir,
                root_folder=self.root_folder,
                file_path=file_path,
                docs=documentation
            )

            # 6. Add the file path and its according documentation to the cache
            cache.add(file_path, docs_filepath)

        # 7. Save cache to a file
        utils.save_cache(self.output_dir, cache)

        total = round(time.time() - start_time, 3)
        print(f'Generated documentation ({cache.size()} files) can be found in {self.output_dir}')
        print(f"Documentation generation completed in {total}s.")

# Test this script
repo_doc = RepoDocumentation(
    llm_id="mistral",
    root_folder="../simple-users/",
    output_dir="docs_output"
)
repo_doc.run()