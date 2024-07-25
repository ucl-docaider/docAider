import time, os, sys, git
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)
from dotenv import load_dotenv
load_dotenv(dotenv_path="../../.env")
from enum import Enum

from repo_agents.documentation_update.update_assistant import UpdateAssistant
from repo_documentation import utils as doc_utils
from repo_agents.documentation_update import git_utils
from cache.document import sha256_hash
from repo_documentation.merging.merger import create_documentation

class ChangeType(Enum):
  ADDED = 'A'
  DELETED = 'D'
  RENAMED = 'R'
  MODIFIED = 'M'

class DocumentationUpdateAgent:
  def __init__(self, repo_path, branch, file_path=None, comment=None, save_debug=False):
    self.root_folder = os.path.abspath(repo_path)
    self.output_folder = os.path.join(self.root_folder, "docs_output")
    self.repo = git.Repo(self.root_folder)
    self.branch = branch
    self.file_path = file_path
    self.comment = comment
    self.save_debug = save_debug
    
    self.ua = UpdateAssistant(
      root_folder=self.root_folder,
      output_folder=self.output_folder,
      save_debug=self.save_debug
    )
    self.cache = doc_utils.get_cache(self.output_folder)

  def update_documentation(self) -> None:
    """
    This is the execution function for the streamlined process of documentation update
    """
    branch_latest_commit_sha = git_utils.get_latest_commit_sha(self.repo, self.branch)
    main_latest_commit_sha = git_utils.get_latest_commit_sha(self.repo, 'main')

    branch_latest_commit = self.repo.commit(branch_latest_commit_sha)
    main_latest_commit = self.repo.commit(main_latest_commit_sha)
    if self.file_path and self.comment:
      print("Updating documentation based on PR comment...")
      abs_file_path = os.path.join(self.root_folder, self.file_path)
      print(f"File path: {abs_file_path}")
      self.ua.update_documentation_based_on_comment(abs_file_path, self.comment, branch_latest_commit)
    else:
      print("Updating documentation based on branch changes...")
      diffs = git_utils.get_diffs(branch_latest_commit, main_latest_commit)
      # Exit if no Python file changes are found
      if not diffs:
        print("No Python file changes found between main and the current branch.")
        return
      
      # Sort diffs by number of parent dependencies, so that we update the leaves first
      diffs = [(diff, self.ua.get_changes(diff, main_latest_commit, branch_latest_commit)) for diff in diffs]
      diffs.sort(key=lambda x: self.ua.get_parents_count(self.ua.get_file_path(x[0]), x[1]))

      # Update the documentation for each Python file that has changed
      for diff, changes in diffs:
        path = self.ua.get_file_path(diff)
        # Attempt to get the cached documentation for the file
        cached_doc = self.cache.get(path)
        change_type = ChangeType(diff.change_type)
        new_commit_content = git_utils.get_file_commit_content(self.root_folder, path, branch_latest_commit)

        # Generate new documentation if the file is not cached
        if change_type == ChangeType.ADDED:
          self.ua.create_documentation_for_file(path, branch_latest_commit)
        # Skip if the file has not been modified since last update
        elif cached_doc and cached_doc.source_file_hash == sha256_hash(new_commit_content):
          print(f'Skipping documentation update for file={path} as it has not been modified since last update.')
        # If the file has been modified, update the documentation
        elif change_type == ChangeType.MODIFIED:
          self.ua.update_documentation_for_file(
            file_path=path,
            main_commit=main_latest_commit,
            branch_commit=branch_latest_commit,
            changes=changes
          )
        # If the file has been renamed
        elif change_type == ChangeType.RENAMED:
          # TODO: Handle renamed files
          pass
        # 6e. If the file has been deleted
        elif change_type == ChangeType.DELETED:
          self.ua.delete_documentation_for_file(path)

      create_documentation(self.output_folder)