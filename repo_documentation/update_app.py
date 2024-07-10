import git_utils
import os
import sys
import time
import git

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from repo_documentation.prompt import PARENT_UPDATE
from code2flow.code2flow import ast_utils
from code2flow.code2flow import utils as code2flow_utils
from autogen_utils import utils as autogen_utils
from repo_documentation import utils
from cache.document import sha256_hash

class DocumentationUpdate():
    def __init__(self, repo_path, branch):
        self.root_folder = os.path.abspath(repo_path)
        self.output_dir = os.path.join(self.root_folder, "docs_output")
        self.repo = git.Repo(self.root_folder)
        self.branch = branch

    def run(self):
        # 1. Get the latest commit of the current branch and the main branch
        curr_branch_sha = git_utils.get_latest_commit_sha(
            self.repo, self.branch)
        main_branch_sha = git_utils.get_latest_commit_sha(self.repo, 'main')

        curr_branch_commit = self.repo.commit(curr_branch_sha)
        main_branch_commit = self.repo.commit(main_branch_sha)

        # 2. Find the diffs between the current branch and main
        diffs = git_utils.get_diffs(curr_branch_commit, main_branch_commit)

        # Exit if no Python file changes are found
        if not diffs:
            print("No Python file changes found between main and the current branch.")
            return

        # 3. Initialize the necessary dependencies for the documentation update process
        self._initialize()
        print("Starting the documentation update process...")
        start_time = time.time()

        # Sort diffs by number of parent dependencies, so that we update the leaves first
        diffs = [(diff, self._get_changes(diff, main_branch_commit, curr_branch_commit)) for diff in diffs]
        diffs.sort(key=lambda x: self._parents_count(self._file_path(x[0]), x[1]))

        # 4. Update the documentation for each Python file that has changed
        for diff, changes in diffs:
            path = self._file_path(diff)

            # Attempt to get the cached documentation for the file
            cached = self.cache.get(path)

            # 6a. Generate new documentation if the file is not cached
            if not cached:
                self._create_docs(path, curr_branch_commit)

            # 6b. Skip if the file has not been modified since last update
            elif cached.source_file_hash == sha256_hash(self._new_content(path, curr_branch_commit)):
                print(f'Skipping documentation update for file={
                      path} as it has not been modified since last update.')

            # 6c. Otherwise update the documentation
            else:
                print(f"Updating documentation for file={path}")
                self._update_docs(file_path=path,
                                  main_branch_commit=main_branch_commit,
                                  current_branch_commit=curr_branch_commit,
                                  changes=changes)

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

    def _get_old_file_docs(self, cache, file_path):
        cached_docs_path = cache.get(file_path).generated_docs_path
        return utils.read_file_content(cached_docs_path)

    def _changes_to_string(self, changes):
        return '\n'.join([f'- {str(change)}' for change in changes])

    def _file_path(self, diff):
        path = os.path.join(self.root_folder, diff.a_path)
        path = os.path.abspath(path)
        return path

    def _new_content(self, file_path, current_branch_commit):
        return git_utils.get_file__commit_content(self.root_folder, file_path, current_branch_commit)

    def _create_docs(self, file_path, current_branch_commit):
        print(f"Generating documentation for file={file_path}")
        # 1. Get the file content
        content = git_utils.get_file__commit_content(self.root_folder,
                                                     file_path, current_branch_commit)

        # 2. Prepare additional context for LLM
        additional_docs = autogen_utils.get_additional_docs_path(
            file_path, self.graph, self.bfs_explore)

        # 3. Generate the documentation for the file
        docs = autogen_utils.get_documentation(
            file_path=file_path,
            file_content=content,
            additional_docs=additional_docs,
            user=self.user,
            assistant=self.assistant,
            output_dir=self.output_dir,
            root_folder=self.root_folder,
            save_debug=True
        )

        # 4. Write the generated documentation to the output directory and save to cache
        self._write_docs_and_cache(file_path, content, docs)

    def _get_changes(self, diff, main_branch_commit, curr_branch_commit):
        path = self._file_path(diff)
        old_content = git_utils.get_file__commit_content(self.root_folder, path, main_branch_commit)
        new_content = git_utils.get_file__commit_content(self.root_folder, path, curr_branch_commit)
        return  ast_utils.get_function_changes(path, old_content, new_content)
    
    def _parents_count(self, path, changes):
        filtered = ast_utils.filter_changes(changes)
        parent_dependencies = code2flow_utils.get_parent_dependencies(
            self.graph, filtered, path)
        return len(parent_dependencies)

    def _update_docs(self, file_path,
                     main_branch_commit,
                     current_branch_commit,
                     changes,
                     additional_functions_info=None):
        # 1. Get the file contents from the main and current branch
        old_content = git_utils.get_file__commit_content(self.root_folder,
                                                         file_path, main_branch_commit)
        new_content = git_utils.get_file__commit_content(self.root_folder,
                                                         file_path, current_branch_commit)

        # 2. Get the unified diff between the old and new file contents
        diff = git_utils.get_unified_diff(old_content, new_content)

        # 3. Find out all the relevant changes in the functions
        filtered = ast_utils.filter_changes(changes)
        parent_dependencies = code2flow_utils.get_parent_dependencies(
            self.graph, filtered, file_path)

        # 5. Prepare additional context for LLM
        additional_docs = autogen_utils.get_additional_docs_path(
            file_path, self.graph, self.bfs_explore)

        if additional_functions_info:
            additional_docs += additional_functions_info

        # 6. Update the documentation based on the diffs and additional docs
        updated_docs = autogen_utils.get_updated_documentation(
            file_path=file_path,
            old_file_docs=self._get_old_file_docs(self.cache, file_path),
            old_file_content=old_content,
            new_file_content=new_content,
            diff=diff,
            additional_docs=additional_docs,
            changes=self._changes_to_string(changes),
            user=self.user,
            assistant=self.assistant,
            output_dir=self.output_dir,
            save_debug=True
        )

        # 7. Write the updated documentation to the output directory and save to cache
        self._write_docs_and_cache(file_path, new_content, updated_docs)

        # 8. For each parent dependency (file -> all functions affected by changes), update docs
        for path, functions in parent_dependencies.items():
            self._update_parent(path, current_branch_commit, main_branch_commit,
                                new_content, filtered, functions)

    def _update_parent(self, path, curr_branch_commit, main_branch_commit,
                       new_content, filtered, functions):
        cached = self.cache.get(path)
        assert cached is not None, f"File {path} not found in cache."

        # Skip cached
        if cached.source_file_hash == sha256_hash(self._new_content(path, curr_branch_commit)):
            print(f'Skipping parent documentation update for file={
                  path} as it has not been modified since last update.')
            return

        print(f'Updating parent dependency for file={path}')

        # Prepare additional functions info for the prompt
        additional_functions_info = PARENT_UPDATE.format(
            filtered=filtered,
            new_content=new_content,
            path=path,
            functions=functions
        )

        # Update the documentation for the dependency
        self._update_docs(file_path=path,
                          main_branch_commit=main_branch_commit,
                          current_branch_commit=curr_branch_commit,
                          additional_functions_info=additional_functions_info)

    def _write_docs_and_cache(self, file_path, content, docs):
        # Write the updated documentation to the output directory
        updated_docs_path = utils.write_file_docs(output_dir=self.output_dir,
                                                  root_folder=self.root_folder,
                                                  file_path=file_path,
                                                  docs=docs)

        # 7. Update the cache with the new documentation path and save
        self.cache.update_docs(file_path, content, updated_docs_path)
        utils.save_cache(self.output_dir, self.cache)


repo_path = "../simple-users/"
branch = "feature"
repo_doc_updater = DocumentationUpdate(
    repo_path=repo_path,
    branch=branch)
repo_doc_updater.run()
