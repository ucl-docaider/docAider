import os, sys, time, datetime, asyncio
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from rag.generator import DocumentationGenerator
from code2flow.code2flow import utils

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
        self.output_dir = output_dir
        self.documentation_generator = DocumentationGenerator(llm_id)

    def run(self):
        """
        The core function of generating documentation.
        Call this function to start the documentation generation process
        """
        print("Starting the documentation generation process...")
        start_time = time.time()

        # 1. Generate graph (call_graph.json and cache.json)
        utils.generate_graph(self.root_folder, self.output_dir)
        cache = utils.get_cache(self.output_dir)
        graph = utils.get_call_graph(self.output_dir)

        # 2. Build mapping of a file to the functions called within them
        file_to_calls = utils.get_file_to_functions(graph)

        # 3. Build BFS exploration of the call graph
        bfs_explore = utils.explore_call_graph(graph)

        # 4. Generate documentation for each file and function within
        for file_path, calls in file_to_calls.items():
            print(f"Generating documentation for file={file_path}")
            if file_path == 'EXTERNAL':
                continue

            # Semantic search for getting source code of the file path
            source_code = asyncio.run(
                self.documentation_generator.retriever.search(query=f"{file_path}")
            )
            additional_docs = self._generate_additional_docs(calls, graph, bfs_explore)
            documentation = asyncio.run(self.documentation_generator.generate_documentation(
                file_path=file_path,
                file_content=source_code,
                root_folder=self.root_folder,
                additional_docs=additional_docs
            ))
            # Create output files
            self._create_prompt_txt_file(self.documentation_generator.prompt, os.path.basename(file_path))
            self._create_documentation_md_file(documentation, file_path)

        # 5. Write the generated documentation back to the cache file
        utils.write_json(f'{self.output_dir}/cache_docs.json', cache)

        total = round(time.time() - start_time, 3)
        print(f"Total time taken to execute doc generation: {total}s.")

    def _generate_additional_docs(self, calls, graph, bfs_explore):
        additional_docs = ""
        for call_name in calls:
            call = graph[call_name]
            if 'EXTERNAL' in call['file_name']:
                continue
            for callee in bfs_explore[call_name]:
                callee_call = graph[callee]
                additional_docs += f"\nFunction/Class {callee_call['name']}:\n{callee_call['content']}\n"
        return additional_docs
    
    def _create_prompt_txt_file(self, prompt, file_name):
        """
        This function saves the prompt message to a text file.

        Args:
            prompt: the prompt message.
            file_name: the file name without the extension name.
        """
        prompt_txt_file = self.output_dir + "/" + file_name + ".txt"
        with open(prompt_txt_file, 'w') as file:
            file.write(prompt)

    def _create_documentation_md_file(self, documentation, file_path):
        """
        This function writes the generated documentation to output file.

        Args:
            documentation: the generated documentation
            file_path: the path of the file
        """
        # Generate the output file path based on the input file path
        relative_path = os.path.relpath(file_path, self.root_folder)
        output_file_path = os.path.join(self.output_dir, relative_path)
        output_dir = os.path.dirname(output_file_path)
        os.makedirs(output_dir, exist_ok=True)

        # Add .md extension to the output file
        output_file_path += ".md"

        # Write the documentation to the output file
        with open(output_file_path, 'w') as file:
            file.write(documentation)

    def _generate_docs_internal(self, name):
        return f'(empty docs for {name})'

    def _generate_docs_external(self, name, graph, cache, file_path, source_code, callees_dict):
        """
        TODO: Complete functionality description of this function
        
        Returns:LLM generated documentation for the source code
        """
        print(f"Generating documentation for function={name}")
        additional_docs = ""

        # 0. Check for cache-hit
        cached_docs = cache.get(name, None)

        # 1. Open the file and read all of its contents for additional documentation, as needed
        file = open(file_path, 'r')

        for item in callees_dict:
            call = graph[item]  # Access the call information
            call_name = call['name']
            
            if 'EXTERNAL' in call_name:
                # TODO: additional_docs += (handle external functions here)
                continue
            
            call_source_code = call['content']
            call_callees = call['callees']
            call_parent_file = open(call['file_name'], 'r')

            # TODO: Here we could either read the entire file or just the function/class definition
            additional_docs += f"\nFunction/Class {call_name}:\n{call_source_code}\n"

            # Close the file
            call_parent_file.close()
        file.close()

        # Call the generator to generate documentation
        response = asyncio.run(self.documentation_generator.generate_documentation(
            file_name=file_path,
            file_content=source_code,
            root_folder=self.root_folder,
            additional_docs=additional_docs
        ))
        return response

    # TODO: Change the implementation as required
    def _update_cache(self, cache, function_name, docs):
        if function_name not in cache:
            cache[function_name] = {}
        cache[function_name]['version'] = 1
        cache[function_name]['generated_on'] = datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')
        cache[function_name]['generated_docs'] = docs

# Test this script
repo_doc = RepoDocumentation(
    llm_id="mistral",
    root_folder="../code2flow/projects/users",
    output_dir="./../code2flow_output_users"
)
repo_doc.run()