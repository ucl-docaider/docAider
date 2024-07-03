import os
import time
import difflib
import git
from autogen import AssistantAgent, UserProxyAgent
from prompt import DOCUMENTATION_UPDATE_PROMPT, USR_PROMPT
from code2flow.code2flow import utils

class DocumentationUpdate():
    __llm_config = {
        "model": "llama3",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    }

    def __init__(self, repo_path, branch, root_folder, output_dir='docs_output'):
        self.repo_path = repo_path
        self.branch = branch
        self.root_folder = root_folder
        self.output_dir = output_dir
        self.repo = git.Repo(repo_path)
        self.commit_sha = self._get_latest_commit_sha()
        self.assistant = self._load_assistant_agent()
        self.user = self._load_user_agent()

    def _get_latest_commit_sha(self):
        # Fetch the latest commit SHA on the specified branch
        branch_ref = self.repo.heads[self.branch]
        latest_commit = branch_ref.commit
        return latest_commit.hexsha

    def _get_previous_non_doc_commit(self, commit):
        # Traverse commit history to find the previous non-documentation update commit
        while commit:
            if "Update documentation" not in commit.message:
                return commit
            if commit.parents:
                commit = commit.parents[0]
            else:
                break
        return None

    def run(self):
        print("Starting the documentation update process...")
        start_time = time.time()

        # Generate graph (call_graph.json and cache.json)
        utils.generate_graph(self.root_folder, self.output_dir)
        cache = utils.get_cache(self.output_dir)
        graph = utils.get_call_graph(self.output_dir)

        # Build BFS exploration of the call graph
        bfs_explore = utils.explore_call_graph(graph)

        # Fetch commit details
        latest_commit = self.repo.commit(self.commit_sha)
        parent_commit = self._get_previous_non_doc_commit(latest_commit)  

        if not parent_commit:
            print("No valid parent commit found for updating documentation.")
            return

        # Iterate over the diffs between the commit and its parent
        for diff in latest_commit.diff(parent_commit):
            file_path = diff.a_path
            print(f"Updating documentation for file={file_path}")

            # 1. Get the old and new file contents
            old_file_content = self._get_file_content(file_path, parent_commit)
            new_file_content = self._get_file_content(file_path, latest_commit)

            # 2. Get the old documentation
            old_file_docs = self._get_old_file_docs(file_path)

            # 3. Generate the diff between old and new file contents
            diff_content = self._generate_diff(old_file_content, new_file_content)

            # 4. Generate additional docs using the call graph
            additional_docs = self._generate_additional_docs(file_path, graph, bfs_explore)

            # 5. Update the documentation based on the diffs and additional docs
            updated_docs = self._update_file_docs(file_path, old_file_docs, old_file_content, new_file_content, diff_content, additional_docs)

            # 6. Write the updated documentation to the output directory
            self._write_file_docs(file_path, updated_docs)

        total = round(time.time() - start_time, 3)
        print(f"Total time taken to execute doc update: {total}s.")

    def _load_assistant_agent(self):
        # Load the assistant agent for LLM-based documentation generation
        return AssistantAgent(
            name="assistant",
            system_message=USR_PROMPT,
            llm_config=self.__llm_config,
            human_input_mode="NEVER"
        )

    def _load_user_agent(self):
        # Load the user agent for LLM-based documentation generation
        return UserProxyAgent(
            name="user",
            code_execution_config=False,
        )

    def _get_file_content(self, file_path, commit):
        # Get the content of the file at a specific commit
        try:
            blob = commit.tree / file_path
            return blob.data_stream.read().decode('utf-8')
        except KeyError:
            return ""

    def _get_old_file_docs(self, file_path):
        # Get the old documentation content for the file
        doc_path = self._get_old_doc_path(file_path)
        print(f"Reading old documentation file: {doc_path}")
        try:
            with open(doc_path, 'r') as file:
                content = file.read()
                return content
        except FileNotFoundError:
            return ""

    def _generate_diff(self, old_content, new_content):
        # Generate the diff between the old and new file contents
        diff = difflib.unified_diff(old_content.splitlines(), new_content.splitlines())
        return "\n".join(diff)

    def _generate_additional_docs(self, file_path, graph, bfs_explore):
        # Generate additional documentation using the call graph and BFS exploration
        additional_docs = ""
        file_to_calls = utils.get_file_to_functions(graph)
        if file_path in file_to_calls:
            calls = file_to_calls[file_path]
            for call_name in calls:
                call = graph[call_name]
                if 'EXTERNAL' in call['file_name']:
                    continue
                for callee in bfs_explore[call_name]:
                    callee_call = graph[callee]
                    additional_docs += f"\nFunction/Class {callee_call['name']}:\n{callee_call['content']}\n"
        return additional_docs

    def _update_file_docs(self, file_path, old_file_docs, old_file_content, new_file_content, diff, additional_docs):
        # Update the file documentation using the old docs, diffs, and additional docs
        prompt_message = DOCUMENTATION_UPDATE_PROMPT.format(
            file_name=os.path.basename(file_path),
            old_file_docs=old_file_docs,
            old_file_content=old_file_content,
            new_file_content=new_file_content,
            diff=diff,
            additional_docs=additional_docs
        )

        self.user.initiate_chat(
            self.assistant,
            message=prompt_message,
            max_turns=1,
            silent=True
        )

        file_name = self.output_dir + "/" + os.path.basename(file_path) + ".txt"

        with open(file_name, 'w') as file:
            file.write(prompt_message)

        return self.assistant.last_message()['content']

    def _write_file_docs(self, file_path, docs):
        # Write the updated documentation to the output directory
        relative_path = os.path.relpath(file_path, self.root_folder)
        output_file_path = os.path.join(self.output_dir, relative_path)
        output_dir = os.path.dirname(output_file_path)
        os.makedirs(output_dir, exist_ok=True)

        output_file_path += ".md"

        with open(output_file_path, 'w') as file:
            file.write(docs)

    def _get_old_doc_path(self, file_path):
        # Get the path to the old documentation file
        relative_path = os.path.relpath(file_path, self.root_folder)
        return os.path.join(self.output_dir, relative_path + ".md")

# Example usage
repo_path = "/path/to/local/repo"
branch = "main"
root_folder = '../code2flow/projects/users'
repo_doc_updater = DocumentationUpdate(
    repo_path=repo_path,
    branch=branch,
    root_folder=root_folder,
    output_dir='../docs_output')
repo_doc_updater.run()
