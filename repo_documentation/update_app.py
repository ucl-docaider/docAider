import difflib
import git_utils
import os
import sys
import time
import git

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from repo_documentation import utils
from autogen_utils import utils as autogen_utils
from code2flow.code2flow import utils as code2flow_utils

class DocumentationUpdate():
    def __init__(self, repo_path, branch):
        self.root_folder = os.path.abspath(repo_path)
        self.output_dir = os.path.join(self.root_folder, "docs_output")
        self.repo = git.Repo(self.root_folder)
        self.branch = branch

    def run(self):
        # 1. Get the latest commit of the current branch and the main branch
        current_branch_sha = git_utils.get_latest_commit_sha(
            self.repo, self.branch)
        main_branch_sha = git_utils.get_latest_commit_sha(self.repo, 'main')

        current_branch_commit = self.repo.commit(current_branch_sha)
        main_branch_commit = self.repo.commit(main_branch_sha)

        # 2. Find the diffs between the current branch and main
        diffs = git_utils.get_diffs(current_branch_commit, main_branch_commit)

        # Exit if no Python file changes are found
        if not diffs:
            print("No Python file changes found between main and the current branch.")
            return
        print(
            f'Found {len(diffs)} Python file changes between main and the current branch.')

        # 3. Initialize the necessary dependencies for the documentation update process
        self._initialize()
        file_to_functions = code2flow_utils.get_file_to_functions(self.graph)
        print("Starting the documentation update process...")
        start_time = time.time()

        # 4. Update the documentation for each Python file that has changed
        for diff in diffs:
            file_path = os.path.join(self.root_folder, diff.a_path)
            file_path = os.path.abspath(file_path)
            print(f"Processing file: {file_path}")
            print(f"Updating documentation for file={file_path}")

            # Get the old and new file contents
            old_file_content = git_utils.get_file__commit_content(self.root_folder,
                                                                  file_path, main_branch_commit)
            new_file_content = git_utils.get_file__commit_content(self.root_folder,
                                                                  file_path, current_branch_commit)

            # Attempt to get the cached documentation for the file
            cached = self.cache.get(file_path)

            # 5. Generate additional docs using the call graph
            additional_docs = autogen_utils.get_additional_docs_path(
                file_path, self.graph, self.bfs_explore)

            # 6a. Generate new documentation if the file is not cached
            if not cached:
                autogen_utils.get_documentation(
                    file_path=file_path,
                    file_content=new_file_content,
                    additional_docs=additional_docs,
                    user=self.user,
                    assistant=self.assistant,
                    output_dir=self.output_dir,
                    root_folder=self.root_folder,
                    save_debug=True
                )
                continue

            # 6b. Skip if the file has not been modified since last update
            if cached.source_file_hash == hash(new_file_content):
                print(
                    f'File {file_path} has not been modified since last update.')
                continue

            # 6c. Otherwise fetch the old file docs
            old_file_docs = self._get_old_file_docs(self.cache, file_path)

            # 7. Generate the diff between old and new file contents
            diff = git_utils.get_unified_diff(old_content=old_file_content,
                                              new_content=new_file_content)

            # 8. TODO: Get parent dependencies
            closest_matching_functions = self.find_closest_matching_functions(
                file_to_functions[file_path], diff)
            parent_dependencies = code2flow_utils.get_parent_dependencies(
                self.graph, closest_matching_functions)

            # 8. Update the documentation based on the diffs and additional docs
            updated_docs = autogen_utils.get_updated_documentation(
                file_path=file_path,
                old_file_docs=old_file_docs,
                old_file_content=old_file_content,
                new_file_content=new_file_content,
                diff=diff,
                additional_docs=additional_docs,
                user=self.user,
                assistant=self.assistant,
                output_dir=self.output_dir,
                save_debug=True
            )

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

    def _get_old_file_docs(self, cache, file_path):
        cached_docs_path = cache.get(file_path).generated_docs_path
        return utils.read_file_content(cached_docs_path)

    """
    TODO: We need to be able to handle all of these scenarios when updating the documentation:
    Possible scenarios:
    1. Function is updated (should return the original function)
    2. Function is added (should return 'None', as there is no such function in the file yet)
    3. Function is renamed (should return the original function)
    4. Function is removed (should return 'None', as there is no such function in the file anymore)
    
    5. Other scenarios, where functions are not changed (should return -1, special case)
    """

    def find_closest_matching_functions(self, file_functions, diff):
        closest_matches = []

        # Extract function names and their content from the diff
        diff_functions = git_utils.extract_functions_from_diff(diff)

        for diff_func_name, diff_func_content in diff_functions.items():
            best_match = None
            highest_ratio = 0

            for file_func in file_functions:
                entry = self.graph.get(file_func)
                file_func_name = entry['name'].split('::')[-1]
                file_func_content = entry['content']

                # Calculate similarity ratio
                name_ratio = difflib.SequenceMatcher(
                    None, diff_func_name, file_func_name).ratio()
                content_ratio = difflib.SequenceMatcher(
                    None, diff_func_content, file_func_content).ratio()
                ratio = (name_ratio + content_ratio) / 2

                if ratio > highest_ratio:
                    highest_ratio = ratio
                    best_match = file_func

            if best_match:
                closest_matches.append(best_match)

        # Handle case where no functions changed
        if not closest_matches and not diff_functions:
            return [-1]
        return closest_matches


repo_path = "../simple-users/"
branch = "feature"
repo_doc_updater = DocumentationUpdate(
    repo_path=repo_path,
    branch=branch)
repo_doc_updater.run()
