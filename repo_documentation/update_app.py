import os
import sys
import time
import difflib
import git
from autogen import AssistantAgent, UserProxyAgent
from prompt import DOCUMENTATION_UPDATE_PROMPT, USR_PROMPT

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

import config
from cache.docs_cache import DocsCache
from code2flow.code2flow import utils


class DocumentationUpdate():
    def __init__(self, repo_path, branch, root_folder, output_dir='docs_output'):
        self.repo_path = os.path.abspath(repo_path)
        self.branch = branch
        self.root_folder = os.path.abspath(root_folder)
        self.output_dir = os.path.abspath(output_dir)
        self.repo = git.Repo(self.repo_path)
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
                return commit.parents[0]
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
        # cache = utils.get_cache(self.output_dir)
        graph = utils.get_call_graph(self.output_dir)

        # Build BFS exploration of the call graph
        bfs_explore = utils.explore_call_graph(graph)

        # Fetch commit details
        latest_commit = self.repo.commit(self.commit_sha)
        parent_commit = self._get_previous_non_doc_commit(latest_commit)  

        # Prepare cache
        cache = self._load_cache(graph)

        if not parent_commit:
            print("No valid parent commit found for updating documentation.")
            return

        # Iterate over the diffs between the commit and its parent
        for diff in latest_commit.diff(parent_commit):
            file_path = diff.a_path
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue  
            
            full_file_path = os.path.join(self.repo_path, file_path)

            # 1. Get the old and new file contents
            old_file_content = self._get_file_content_from_commit(full_file_path, parent_commit)
            new_file_content = self._get_file_content_from_commit(full_file_path, latest_commit)

            # 2. Generate the diff between old and new file contents
            diff_content = self._generate_diff(old_file_content, new_file_content)

            # 3. Generate additional docs using the call graph
            additional_docs = self._generate_additional_docs(full_file_path, graph, bfs_explore)

            # 4. Get the old documentation
            cached_docs = cache.get(full_file_path)
            
            # 5a. If no cached documentation, create new documentation
            if not cached_docs:
                print(f"Creating documentation for file={full_file_path}")
                # If cache miss, create documentation
                # TODO: Implement
                # self._write_file_docs(abs_path, updated_docs)
                continue

            # 5b. If the hash of new file content and cached file content match, skip
            if cached_docs.source_file_hash == hash(new_file_content):
                continue
            
            # 5c. If cache hit, update documentation
            print(f"Updating documentation for file={full_file_path}")
            prev_docs_path = cached_docs.generated_docs_path
            old_source_file = self._read_file_content(cached_docs.source_file_path)
            old_docs_file = self._read_file_content(prev_docs_path)
            updated_docs = self._update_file_docs(full_file_path, old_docs_file, old_source_file, 
                                                    new_file_content, diff_content, additional_docs)
            
            # 6. Write the updated documentation to the output directory
            self._write_file_docs(full_file_path, updated_docs)

        total = round(time.time() - start_time, 3)
        print(f"Total time taken to execute doc update: {total}s.")

    def _load_assistant_agent(self):
        # Load the assistant agent for LLM-based documentation generation
        return AssistantAgent(
            name="assistant",
            system_message=USR_PROMPT,
            llm_config=config.llm_config,
            human_input_mode="NEVER"
        )

    def _load_user_agent(self):
        # Load the user agent for LLM-based documentation generation
        return UserProxyAgent(
            name="user",
            code_execution_config=False,
        )

    def _get_file_content_from_commit(self, file_path, commit):
        # Get the content of the file at a specific commit
        try:
            relative_path = os.path.relpath(file_path, self.repo_path)
            blob = commit.tree / relative_path
            return blob.data_stream.read().decode('utf-8')
        except KeyError:
            return ""

    def _read_file_content(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def _generate_diff(self, old_content, new_content):
        # Generate the diff between the old and new file contents
        diff = difflib.unified_diff(old_content.splitlines(), new_content.splitlines())
        return "\n".join(diff)

    def _generate_additional_docs(self, file_path, graph, bfs_explore):
        # Generate additional documentation using the call graph and BFS exploration
        additional_docs = ""
        relative_path = os.path.relpath(file_path, self.repo_path)
        file_to_calls = utils.get_file_to_functions(graph)
        if relative_path in file_to_calls:
            calls = file_to_calls[relative_path]
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

        return self.assistant.last_message()['content']

    def _write_file_docs(self, file_path, docs):
        # Write the updated documentation to the output directory
        relative_path = os.path.relpath(file_path, self.repo_path)
        output_file_path = os.path.join(self.output_dir, relative_path)
        output_dir = os.path.dirname(output_file_path)
        os.makedirs(output_dir, exist_ok=True)
        output_file_path += ".md"
        with open(output_file_path, 'w') as file:
            file.write(docs)
        print(f"Updated documentation written to: {output_file_path}")

    def _load_cache(self, graph) -> DocsCache:
        cache = DocsCache()
        file_to_calls = utils.get_file_to_functions(graph)
        for file_path, _ in file_to_calls.items():
            if 'EXTERNAL' not in file_path:
                doc_path = self._get_old_doc_path(os.path.basename(file_path))
                if os.path.exists(doc_path):
                    cache.add(file_path, doc_path)
        return cache
    
    def _get_old_doc_path(self, file_path):
        # Get the path to the old documentation file
        return os.path.join(self.output_dir, file_path + ".md")

# Example usage
repo_path = "../simple-users"
branch = "feature"
root_folder = '../simple-users'
repo_doc_updater = DocumentationUpdate(
    repo_path=repo_path,
    branch=branch,
    root_folder=root_folder,
    output_dir='../simple-users/docs_output')
repo_doc_updater.run()
