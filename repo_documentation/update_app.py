import os
import sys
import time
import difflib
import git
from prompt import DOCUMENTATION_UPDATE_PROMPT

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from code2flow.code2flow import utils as code2flow_utils
from autogen_utils import utils as autogen_utils
from repo_documentation import utils

class DocumentationUpdate():
    def __init__(self, repo_path, branch):
        self.branch = branch
        self.root_folder = os.path.abspath(repo_path)
        self.output_dir = os.path.join(self.root_folder, "docs_output")
        self.repo = git.Repo(self.root_folder)
        self.commit_sha = self._get_latest_commit_sha()
        self.assistant = autogen_utils.load_assistant_agent()
        self.user = autogen_utils.load_user_agent()

    def _get_latest_commit_sha(self):
        # Fetch the latest commit SHA on the specified branch
        branch_ref = self.repo.heads[self.branch] # TODO: Handle exception when not found
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
        code2flow_utils.generate_graph(self.root_folder, self.output_dir)
        # cache = utils.get_cache(self.output_dir)
        graph = code2flow_utils.get_call_graph(self.output_dir)

        # Build BFS exploration of the call graph
        bfs_explore = code2flow_utils.explore_call_graph(graph)

        # Fetch commit details
        latest_commit = self.repo.commit(self.commit_sha)
        parent_commit = self._get_previous_non_doc_commit(latest_commit)

        # Load cache
        cache = utils.get_cache(self.output_dir)

        if not parent_commit:
            print("No valid parent commit found for updating documentation.")
            return

        # Iterate over the diffs between the commit and its parent
        for diff in latest_commit.diff(parent_commit):
            file_path = diff.a_path
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue  
            
            full_file_path = os.path.join(self.root_folder, file_path)
            print(f"Processing file: {full_file_path}")
            print(f"Updating documentation for file={full_file_path}")

            # 1. Get the old and new file contents
            old_file_content = self._get_file__commit_content(full_file_path, parent_commit)
            new_file_content = self._get_file__commit_content(full_file_path, latest_commit)
            
            cached = cache.get(full_file_path)
            
            # 2a. Generate new documentation if the file is not cached
            if not cached:
                # TODO: Generate documentation for new files
                continue
            
            # 2b. Skip if the file has not been modified since last update
            if cached.source_file_hash == hash(new_file_content):
                print(f"File {full_file_path} has not been modified since last update.")
                continue

            # 2c. Otherwise fetch the old file docs
            old_file_docs = self._get_old_file_docs(cache, full_file_path)

            # 3. Generate the diff between old and new file contents
            diff_content = self._generate_diff(old_file_content, new_file_content)

            # 4. Generate additional docs using the call graph
            additional_docs = self._generate_additional_docs(full_file_path, graph, bfs_explore)

            # 5. Update the documentation based on the diffs and additional docs
            updated_docs = self._get_updated_docs(full_file_path, old_file_docs, old_file_content, new_file_content, diff_content, additional_docs)

            # 6. Write the updated documentation to the output directory
            updated_docs_path = utils.write_file_docs(output_dir=self.output_dir,
                                    root_folder=self.root_folder,
                                    file_path=full_file_path,
                                    docs=updated_docs)
            
            # 7. Update the cache with the new documentation path and save
            cache.update_docs(full_file_path, updated_docs_path)
            utils.save_cache(self.output_dir, cache)
            
        total = round(time.time() - start_time, 3)
        print(f"Total time taken to execute doc update: {total}s.")

    def _get_file__commit_content(self, file_path, commit):
        # Get the content of the file at a specific commit
        try:
            relative_path = os.path.relpath(file_path, self.root_folder)
            blob = commit.tree / relative_path
            return blob.data_stream.read().decode('utf-8')
        except KeyError:
            return ""

    def _get_old_file_docs(self, cache, file_path):
        old_docs_path = cache.get(file_path).generated_docs_path
        return utils.read_file_content(old_docs_path)

    def _generate_diff(self, old_content, new_content):
        # Generate the diff between the old and new file contents
        diff = difflib.unified_diff(old_content.splitlines(), new_content.splitlines())
        return "\n".join(diff)

    def _generate_additional_docs(self, file_path, graph, bfs_explore):
        # Generate additional documentation using the call graph and BFS exploration
        additional_docs = ""
        file_to_calls = code2flow_utils.get_file_to_functions(graph)
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

    def _get_updated_docs(self, file_path, old_file_docs, old_file_content, new_file_content, diff, additional_docs):
        # Update the file documentation using the old docs, diffs, and additional docs
        prompt_message = DOCUMENTATION_UPDATE_PROMPT.format(
            file_name=os.path.basename(file_path),
            old_file_docs=old_file_docs,
            old_file_content=old_file_content,
            new_file_content=new_file_content,
            diff=diff,
            additional_docs=additional_docs
        )
        autogen_utils.initiate_chat(self.user, self.assistant, prompt_message)
        utils.save_prompt_debug(self.output_dir, file_path, prompt_message, utils.Mode.UPDATE)
        return self.assistant.last_message()['content']
    

repo_path = "../simple-users/"
branch = "feature"
repo_doc_updater = DocumentationUpdate(
    repo_path=repo_path,
    branch=branch)
repo_doc_updater.run()