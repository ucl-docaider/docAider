import json
import os
import datetime
import sys
import time
from autogen import AssistantAgent, UserProxyAgent
from prompt import DOCUMENTATION_PROMPT, USR_PROMPT

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))
from code2flow.code2flow import code2flow

class RepoDocumentation():
    __llm_config = {
        "model": "llama3",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    }

    def __init__(self, root_folder, output_dir='code2flow_output'):
        self.root_folder = root_folder
        self.output_dir = output_dir
        self.assistant = self._load_assistant_agent()
        self.user = self._load_user_agent()

    def _load_assistant_agent(self):
        return AssistantAgent(
            name="assistant",
            system_message=USR_PROMPT,
            llm_config=self.__llm_config,
            human_input_mode="NEVER"
        )

    def _load_user_agent(self):
        return UserProxyAgent(
            name="user",
            code_execution_config=False,
        )

    def run(self):
        print("Starting the documentation generation process...")
        start_time = time.time()

        # 1. Generate graph (call_graph.json and cache.json)
        self._generate_graph()
        graph = self._load_json(f'{self.output_dir}/call_graph.json')
        cache = self._load_json(f'{self.output_dir}/cache.json')

        # 2. Build mapping of a file to the functions called within them
        file_to_calls = self._get_file_to_function_map(graph)

        # 3. Generate documentation for each function
        for file_path, calls in file_to_calls.items():
            for call in calls:
                # Skip external functions
                if 'EXTERNAL' in call:
                    print(f"Skipping external function: {call}")
                    continue

                call = graph[call]
                name = call['name']
                source_code = call['content']

                # Core functionality to generate documentation
                docs = self._generate_function_doc(
                    file_path, source_code, call['callees'])

                # Store the generated documentation in the cache (TODO: change impl)
                cache[name]['version'] = 1
                cache[name]['generated_on'] = datetime.datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S')
                cache[name]['source_code'] = source_code
                cache[name]['generated_docs'] = docs

        # 4. Write the generated documentation back to the cache file
        self._write_json(f'{self.output_dir}/cache_generated.json', cache)

        total = round(time.time() - start_time, 3)
        print(f"Total time taken to execute from initiate_chat: {total}s.")

    def _generate_graph(self):
        code2flow(
            raw_source_paths=self.root_folder,
            output_dir=self.output_dir,
            generate_json=True,
            generate_image=True,
            build_cache=True,
        )

    def _generate_function_doc(self, file_name, source_code, called_functions):
        print(f"Generating documentation for {file_name}...")
        additional_docs = ""
        # TODO: Consider callees in docs generation
        # for func in called_functions:
        #     for path, content in file_contents.items():
        #         if f"def {func}(" in content or f"class {func}(" in content:
        #             additional_docs += f"\nFunction/Class {func}:\n{get_code_snippet(os.path.join(root_folder, path), func)}\n"
        #             break

        prompt_message = DOCUMENTATION_PROMPT.format(
            file_name=file_name,
            file_content=source_code,
            root_folder=self.root_folder,
            additional_docs=additional_docs
        )

        self.user.initiate_chat(
            self.assistant,
            message=prompt_message,
            max_turns=1,
            silent=True
        )
        # Return the last message from the assistant, which is the generated documentation
        return self.assistant.last_message()['content']

    def _load_json(self, file_path):
        with open(file_path, 'r') as f:
            return json.load(f)

    def _write_json(self, file_path, data):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def _get_file_to_function_map(self, graph):
        """
        {
            'file1.py': ['func1', 'func2'],
            'file2.py': ['func3', 'func4'],
            'EXTERNAL': ['EXTERNAL::dict', 'EXTERNAL::list'], 
            ...
        }
        """
        file_to_calls = {}
        for method_name, call in graph.items():
            file_name = call['file_name']
            items = file_to_calls.get(file_name, [])
            file_to_calls[file_name] = items + [method_name]
        return file_to_calls


repo_doc = RepoDocumentation(
    root_folder='../code2flow/projects/simple',
    output_dir='code2flow_output')
repo_doc.run()