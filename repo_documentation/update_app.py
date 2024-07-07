import os
import sys
import time
import difflib
import git
from prompt import DOCUMENTATION_UPDATE_PROMPT

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from repo_documentation import utils
from autogen_utils import utils as autogen_utils
from code2flow.code2flow import utils as code2flow_utils

class DocumentationUpdate():
    def __init__(self, repo_path, branch):
        self.branch = branch
        self.root_folder = os.path.abspath(repo_path)
        self.output_dir = os.path.join(self.root_folder, "docs_output")
        self.repo = git.Repo(self.root_folder)
        self.commit_sha = self._get_latest_commit_sha()
        self.assistant = None
        self.user = None
        self.cache = None
        self.graph = None
        self.bfs_explore = None

    def run(self):
        # 1. Fetch the latest commit and first non-documentation parent commit
        latest_commit = self.repo.commit(self.commit_sha)
        parent_commit = self._get_previous_non_doc_commit(latest_commit)

        # Exit if no valid parent commit is found
        if not parent_commit:
            raise Exception(
                "No valid parent commit found for updating documentation.")

        # 2. Find the diffs between the latest commit and its parent
        diffs = self._get_diffs(latest_commit, parent_commit)

        # Exit if no Python file changes are found in the commit
        if not diffs:
            print("No Python file changes found in the commit.")
            return
        print(f'Found {len(diffs)} Python file changes in the commit.')

        # 3. Initialize the necessary dependencies for the documentation update process
        self._initialize()
        print("Starting the documentation update process...")
        start_time = time.time()

        # 4. Update the documentation for each Python file in the commit
        for diff in diffs:
            file_path = os.path.join(self.root_folder, diff.a_path)
            file_path = os.path.abspath(file_path)
            print(f"Processing file: {file_path}")
            print(f"Updating documentation for file={file_path}")

            # Get the old and new file contents
            old_file_content = self._get_file__commit_content(
                file_path, parent_commit)
            new_file_content = self._get_file__commit_content(
                file_path, latest_commit)

            # Attempt to get the cached documentation for the file
            cached = self.cache.get(file_path)

            # 5a. Generate new documentation if the file is not cached
            if not cached:
                # TODO: Generate documentation for new files
                continue

            # 5b. Skip if the file has not been modified since last update
            if cached.source_file_hash == hash(new_file_content):
                print(
                    f"File {file_path} has not been modified since last update.")
                continue

            # 5c. Otherwise fetch the old file docs
            old_file_docs = self._get_old_file_docs(self.cache, file_path)

            # 6. Generate the diff between old and new file contents
            diff = self._generate_diff(old_file_content, new_file_content)

            # 7. Generate additional docs using the call graph
            additional_docs = self._generate_additional_docs(
                file_path, self.graph, self.bfs_explore)

            # 8. Update the documentation based on the diffs and additional docs
            updated_docs = self._get_updated_docs(file_path=file_path,
                                                  old_file_docs=old_file_docs,
                                                  old_file_content=old_file_content,
                                                  new_file_content=new_file_content,
                                                  diff=diff,
                                                  additional_docs=additional_docs)

            # 9. Write the updated documentation to the output directory
            updated_docs_path = utils.write_file_docs(output_dir=self.output_dir,
                                                      root_folder=self.root_folder,
                                                      file_path=file_path,
                                                      docs=updated_docs)

            # 10. Update the cache with the new documentation path and save
            self.cache.update_docs(file_path, updated_docs_path)
            utils.save_cache(self.output_dir, self.cache)

        total = round(time.time() - start_time, 3)
        print(f"Total time taken to execute doc update: {total}s.")

    def _initialize(self):
        """
        Initialize all necessary dependencies for the documentation update process.
        The reason for this method is to ensure that all dependencies are only initialized
        when required, and not if there are no new changes in the repository.

        The following dependencies are initialized:
        - Assistant Agent
        - User Agent
        - Graph & Call Graph
        - BFS Exploration
        - Cache
        """
        # Load assistants
        self.assistant = autogen_utils.load_assistant_agent()
        self.user = autogen_utils.load_user_agent()

        # Generate graph
        code2flow_utils.generate_graph(self.root_folder, self.output_dir)
        self.graph = code2flow_utils.get_call_graph(self.output_dir)

        # Build BFS exploration of the call graph
        self.bfs_explore = code2flow_utils.explore_call_graph(self.graph)

        # Load cache
        self.cache = utils.get_cache(self.output_dir)

    def _get_latest_commit_sha(self):
        """
        Get the SHA of the latest commit on the specified branch.
        Raises exception if the specified branch is not found in the repository.
        """
        if self.branch not in self.repo.heads:
            raise Exception(
                f'Branch {self.branch} not found in the repository.')
        branch_ref = self.repo.heads[self.branch]
        latest_commit = branch_ref.commit
        return latest_commit.hexsha

    def _get_previous_non_doc_commit(self, commit):
        """
        Gets the previous non-documentation commit from the given commit.
        """
        while commit:
            if "Update documentation" not in commit.message:
                return commit.parents[0]
            if commit.parents:
                commit = commit.parents[0]
            else:
                break
        return None

    def _get_diffs(self, commit, parent):
        """
        Find all the Python file diffs between the commit and its parent.
        """
        diffs = commit.diff(parent)
        python_diffs = []
        for diff in diffs:
            file_path = diff.a_path
            if file_path.endswith('.py'):
                python_diffs.append(diff)
        return python_diffs

    def _get_file__commit_content(self, file_path, commit):
        """
        Get the content of a file at a specific commit.

        Args:
            file_path (str): The path of the file.
            commit (Commit): The specific commit to retrieve the file content from.

        Returns the content of the file at the specified commit. 
        If the file does not exist, an empty string is returned.
        """
        try:
            relative_path = os.path.relpath(file_path, self.root_folder)
            blob = commit.tree

            # Split the path and traverse the tree
            for part in relative_path.split(os.path.sep):
                blob = blob[part]

            # If it's a blob, return its content
            if blob.type == 'blob':
                return blob.data_stream.read().decode('utf-8')
            else:
                # If it's not a blob (e.g., it's a tree), return an empty string
                return ''
        except KeyError:
            return ''

    def _get_old_file_docs(self, cache, file_path):
        """
        Retrieves the old file documentation from the cache.
        """
        cached_docs_path = cache.get(file_path).generated_docs_path
        return utils.read_file_content(cached_docs_path)

    def _generate_diff(self, old_content, new_content):
        """
        Generate a unified diff between the old and new file contents.
        """
        diff = difflib.unified_diff(
            old_content.splitlines(), new_content.splitlines())
        return "\n".join(diff)

    def _generate_additional_docs(self, file_path, graph, bfs_explore):
        """
        Generate additional documentation using the call graph and BFS exploration.
        """
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
                    additional_docs += f"\nFunction/Class {
                        callee_call['name']}:\n{callee_call['content']}\n"
        return additional_docs

    def _get_updated_docs(self, file_path, old_file_docs,
                          old_file_content, new_file_content,
                          diff, additional_docs):
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
        utils.save_prompt_debug(
            self.output_dir, file_path, prompt_message, utils.Mode.UPDATE)
        return self.assistant.last_message()['content']


repo_path = "../simple-users/"
branch = "feature"
repo_doc_updater = DocumentationUpdate(
    repo_path=repo_path,
    branch=branch)
repo_doc_updater.run()
