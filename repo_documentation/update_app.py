import git_utils
import os
import sys
import time
import git
from enum import Enum


sys.path.append(os.path.abspath(
	os.path.join(os.path.dirname(__file__), './../')))

from code2flow.code2flow import ast_utils
from code2flow.code2flow import utils as code2flow_utils
from autogen_utils import utils as autogen_utils
from repo_documentation import utils
from cache.document import sha256_hash
import argparse
from repo_documentation.merging.merger import create_documentation

class ChangeType(Enum):
	ADDED = 'A'
	DELETED = 'D'
	RENAMED = 'R'
	MODIFIED = 'M'

class DocumentationUpdate():
	def __init__(self, repo_path, branch, file_path=None, comment=None):
		self.root_folder = os.path.abspath(repo_path)
		self.output_dir = os.path.join(self.root_folder, "docs_output")
		self.repo = git.Repo(self.root_folder)
		self.branch = branch
		self.file_path = file_path
		self.comment = comment

	def run(self):
		if self.file_path and self.comment:
			self._initialize()
			print("Updating documentation based on PR comment...")
			curr_branch_sha = git_utils.get_latest_commit_sha(self.repo, self.branch)
			curr_branch_commit = self.repo.commit(curr_branch_sha)
			abs_file_path = os.path.join(self.root_folder, self.file_path)
			print(f"File path: {abs_file_path}")
			self.update_documentation_based_on_comment(abs_file_path, self.comment, curr_branch_commit)
			if os.getenv("FORMAT") == "html":
				create_documentation
		else:
			print("Updating documentation based on branch changes...")
			# 1. Get the latest commit of the current branch and the main branch
			curr_branch_sha = git_utils.get_latest_commit_sha(self.repo, self.branch)
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
				
				change_type = ChangeType(diff.change_type)

				# 6a. Generate new documentation if the file is not cached
				if change_type == ChangeType.ADDED:
					self._create_docs(path, curr_branch_commit)

				# 6b. Skip if the file has not been modified since last update
				elif cached and cached.source_file_hash == sha256_hash(self._new_commit_content(path, curr_branch_commit)):
					print(f'Skipping documentation update for file={path} as it has not been modified since last update.')
					
				# 6c. If the file has been modified, update the documentation
				elif change_type == ChangeType.MODIFIED:
					self._update_docs(file_path=path, main_branch_commit=main_branch_commit, current_branch_commit=curr_branch_commit, changes=changes)
				# 6d. If the file has been renamed
				elif change_type == ChangeType.RENAMED:
					# TODO: Handle renamed files
					pass
				# 6e. If the file has been deleted
				elif change_type == ChangeType.DELETED:
					self._handle_deleted(path)

			if os.getenv("FORMAT") == "html":
				create_documentation(self.output_dir)	
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

	def _new_commit_content(self, file_path, current_branch_commit):
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
		return ast_utils.get_function_changes(path, old_content, new_content)

	
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
		print(f"Updating documentation for file={file_path}")
		# 1. Get the file contents from the main and current branch
		old_content = git_utils.get_file__commit_content(self.root_folder,
														 file_path, main_branch_commit)
		new_content = git_utils.get_file__commit_content(self.root_folder,
														 file_path, current_branch_commit)

		# 2. Get the unified diff between the old and new file contents
		diff = git_utils.get_unified_diff(old_content, new_content)

		# 3. Find out all the relevant changes in the functions
		filtered = ast_utils.filter_changes(changes)
		print(f'Filtered changes: {filtered}')
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
		print(f'Parent dependencies: {parent_dependencies}')
		for path, functions in parent_dependencies.items():
			new_content = git_utils.get_file__commit_content(self.root_folder,
													path, current_branch_commit)
			self._update_parent(path, current_branch_commit,
								new_content, filtered, functions)

	def _update_parent(self, file_path, curr_branch_commit,
					   new_content, filtered, functions):
		cached = self.cache.get(file_path)
		assert cached is not None, f"File {file_path} not found in cache."

		print(f'Updating parent dependency for file={file_path}')
		print(f"New content for parent dependency: {new_content}")
  
		parent_content = git_utils.get_file__commit_content(self.root_folder,
		 												 file_path, curr_branch_commit)

		# Update the documentation based on the diffs and additional docs


		additional_docs = autogen_utils.get_additional_docs_path(file_path, self.graph, self.bfs_explore)
  
		# Update the documentation based on the diffs and additional docs
		updated_docs = autogen_utils.get_updated_parent_documentation(
			file_path=file_path,
			updated_functions=filtered,
			additional_docs=additional_docs,
			new_content=new_content,
			functions=functions,
			parent_content=parent_content,
			old_parent_docs = self._get_old_file_docs(self.cache, file_path),
			user=self.user,
			assistant=self.assistant,
			output_dir=self.output_dir,
			save_debug=True
		)

		# Write the updated documentation to the output directory and save to cache
		self._write_docs_and_cache(file_path, new_content, updated_docs)

	def _write_docs_and_cache(self, file_path, content, docs):
		# Write the updated documentation to the output directory
		updated_docs_path = utils.write_file_docs(output_dir=self.output_dir,
												  root_folder=self.root_folder,
												  file_path=file_path,
												  docs=docs)

		# 7. Update the cache with the new documentation path and save
		self.cache.update_docs(file_path, content, updated_docs_path)
		utils.save_cache(self.output_dir, self.cache)

	def _handle_deleted(self, file_path):
		print(f"File deleted: {file_path}")
		old_file_docs_path = self.cache.get(file_path).generated_docs_path
		print(f"Old file docs path: {old_file_docs_path}")
		if os.path.exists(old_file_docs_path):
			os.remove(old_file_docs_path)
			print(f"Deleted documentation for {file_path}")


	def update_documentation_based_on_comment(self, file_path, comment, curr_branch_commit):
		# Convert the relative file path to an absolute path		
		new_content = git_utils.get_file__commit_content(self.root_folder,
													file_path, curr_branch_commit)

		# Read the current file content
		with open(file_path, 'r') as f:
			file_content = f.read()

		# Get old documentation
		old_file_docs = self._get_old_file_docs(self.cache, file_path)

		updated_docs = autogen_utils.get_updated_commit_documentation(
			file_path=file_path,
			comment=comment,
			file_content=file_content,
			old_file_docs=old_file_docs,
			user=self.user,
			assistant=self.assistant,
			output_dir=self.output_dir,
			save_debug=True
		)
		# Update cache with new documentation
		self._write_docs_and_cache(file_path, new_content, updated_docs)


if __name__ == "__main__":
	# Parse arguments
	parser = argparse.ArgumentParser(description='Update documentation based on PR comment')
	parser.add_argument('--file', type=str, help='The path of the file to update')
	parser.add_argument('--comment', type=str, help='The comment to base the update on')
	args = parser.parse_args()

	repo_path = "./../../users/"
	branch = "testing2"
	file_path = args.file
	comment = args.comment

	repo_doc_updater = DocumentationUpdate(
		repo_path=repo_path,
		branch=branch,
		file_path=file_path,
		comment=comment
	)
	repo_doc_updater.run()