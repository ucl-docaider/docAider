import time, os, sys, git
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)
from dotenv import load_dotenv
load_dotenv(dotenv_path="../../.env")
from repo_agents.ast_agent import ASTAgent
from repo_agents.documentation_update.update_assistant import UpdateAssistant
from repo_documentation import utils as doc_utils
from repo_agents.documentation_update import git_utils
from repo_documentation.merging.merger import create_documentation

class DocumentationUpdateAgent:
  def __init__(self, repo_path, branch, file_path=None, comment=None, save_debug=False):
    self.root_folder = os.path.abspath(repo_path)
    self.output_folder = os.path.join(self.root_folder, "docs_output")
    self.repo = git.Repo(self.root_folder)
    self.branch = branch
    self.file_path = file_path
    self.comment = comment
    self.save_debug = save_debug
    self.ast_agent = ASTAgent()
    self.update_assistant = UpdateAssistant(
      root_folder=self.root_folder,
      output_folder=self.output_folder,
      save_debug=self.save_debug
    )
    self.cache = doc_utils.get_cache(self.output_folder)

  def update_documentation(self) -> None:
    """
    This is the execution function for the streamlined process of documentation update
    """
    if self.file_path and self.comment:
      print("Updating documentation based on PR comment...")
      branch_latest_commit_sha = git_utils.get_latest_commit_sha(self.repo, self.branch)
      branch_latest_commit = self.repo.commit(branch_latest_commit_sha)
      abs_file_path = os.path.join(self.root_folder, self.file_path)
      print(f"File path: {abs_file_path}")
      self.update_assistant.update_documentation_based_on_comment(abs_file_path, self.comment, branch_latest_commit)
    else:
      print(f"TODO: Update documentation based on branch changes")