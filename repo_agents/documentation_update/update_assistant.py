import os, asyncio
import repo_documentation.utils as doc_utils
from repo_agents.ast_agent import ASTAgent
from repo_agents.chat_completion_agent import ChatCompletionAgent
from repo_agents.documentation_update import git_utils
from code2flow.code2flow import ast_utils
from code2flow.code2flow import utils as code2flow_utils
from repo_agents.prompt import DOCUMENTATION_PROMPT, DOCUMENTATION_UPDATE_PROMPT, PARENT_UPDATE_PROMPT, UPDATE_BY_COMMENT_PROMPT

class UpdateAssistant:
  def __init__(self, root_folder, output_folder, save_debug=False) -> None:
    self.root_folder = root_folder
    self.output_folder = output_folder
    self.chat_completion_agent = ChatCompletionAgent()
    self.ast_agent = ASTAgent()
    self.cache = doc_utils.get_cache(self.output_folder)
    self.save_debug = save_debug

  def update_documentation_based_on_comment(self, file_path, comment, branch_latest_commit) -> None:
    """
    Updates documentation for the file based on PR comment.
    """
    new_content = git_utils.get_file_commit_content(self.root_folder, file_path, branch_latest_commit)
    file_content = doc_utils.read_file_content(file_path)
    old_file_docs = self._get_old_file_docs(file_path)
    prompt = UPDATE_BY_COMMENT_PROMPT.format(
      abs_file_path=file_path,
      comment=comment,
      file_content=file_content,
      old_file_docs=old_file_docs,
    )
    if self.save_debug:
      doc_utils.save_prompt_debug(
        self.root_folder, file_path, prompt, doc_utils.Mode.UPDATE)
    
    # Generate updated documentation
    updated_documentation = asyncio.run(self.chat_completion_agent.generate_response(prompt))
    # Update cache with new documentation
    self._write_docs_and_cache(file_path, new_content, updated_documentation)

  def create_documentation_for_file(self, file_path, current_branch_commit) -> None:
    """
    Create a new documentation for the file.
    Used when the `change_type` of the file is `ADDED`.
    """
    file_content = git_utils.get_file_commit_content(self.root_folder, file_path, current_branch_commit)
    callee_functions = self.ast_agent.get_additional_docs_path(file_path)
    prompt = DOCUMENTATION_PROMPT.format(
      file_name=os.path.basename(file_path),
      file_content=file_content,
      callee_functions=callee_functions
    )
    if self.save_debug:
      doc_utils.save_prompt_debug(
        self.root_folder, file_path, prompt, doc_utils.Mode.UPDATE)

    # Generate new documentation
    documentation = asyncio.run(self.chat_completion_agent.generate_response(prompt))
    # Update cache with new documentation
    self._write_docs_and_cache(file_path, file_content, documentation)

  def update_documentation_for_file(self, file_path, main_commit, branch_commit, changes) -> None:
    """
    Update documentation for the file.
    Used when the `change_type` of the file is `MODIFIED`.
    """
    print(f"Updating documentation for file={file_path}")
    old_content = git_utils.get_file_commit_content(self.root_folder, file_path, main_commit)
    new_content = git_utils.get_file_commit_content(self.root_folder, file_path, branch_commit)
    # Get the unified diff between the old and new file contents
    diff = git_utils.get_unified_diff(old_content, new_content)
    # Get all the relevant changes in the functions
    filtered_changes = ast_utils.filter_changes(changes)

    parent_dependencies = code2flow_utils.get_parent_dependencies(self.ast_agent.graph, filtered_changes, file_path)
    """callee_functions = self.ast_agent.get_additional_docs_path(file_path)
    if callee_function_info:
      callee_functions += callee_function_info""" # Ready to delete

    old_file_docs = self._get_old_file_docs(file_path)
    prompt = DOCUMENTATION_UPDATE_PROMPT.format(
      file_name=os.path.basename(file_path),
      old_file_docs=old_file_docs,
      old_file_content=old_content,
      new_file_content=new_content,
      diff=diff,
      changes=self._changes_to_string(changes)
    )
    if self.save_debug:
      doc_utils.save_prompt_debug(
        self.root_folder, file_path, prompt, doc_utils.Mode.UPDATE)
      
    # Generate updated documentation
    updated_documentation = asyncio.run(self.chat_completion_agent.generate_response(prompt))
    # Update cache with new documentation
    self._write_docs_and_cache(file_path, new_content, updated_documentation)

    # For each parent dependency (file -> all functions affected by changes), update docs
    print(f'Parent dependencies: {parent_dependencies}')
    for path, functions in parent_dependencies.items():
      new_content_of_file = git_utils.get_file_commit_content(self.root_folder, path, branch_commit)
      self.update_parent_documentation(path, branch_commit, new_content_of_file, filtered_changes, functions)

  def update_parent_documentation(self, file_path, branch_commit, new_content, filtered_changes, functions) -> None:
    """
    Update parent documentation. (Triggered by `update_documentation_for_file`)
    """
    cached_file = self.cache.get(file_path)
    assert cached_file is not None, f"File {file_path} not found in cache."

    print(f'Updating parent dependency for file={file_path}')
    print(f"New content for parent dependency: {new_content}")
    parent_content = git_utils.get_file_commit_content(self.root_folder, file_path, branch_commit)
    old_parent_docs = self._get_old_file_docs(file_path)
    callee_functions = self.ast_agent.get_additional_docs_path(file_path)

    prompt = PARENT_UPDATE_PROMPT.format(
      updated_function_contents=filtered_changes,
      callee_functions=callee_functions,
      new_content=new_content,
      file_path=file_path,
      functions=functions,
      parent_content=parent_content,
      old_parent_docs=old_parent_docs
    )
    if self.save_debug:
      doc_utils.save_prompt_debug(
        self.root_folder, file_path, prompt, doc_utils.Mode.UPDATE)

    # Generate updated parent documentation
    updated_parent_documentation = asyncio.run(self.chat_completion_agent.generate_response(prompt))
    # Update cache with updated parent documentation
    self._write_docs_and_cache(file_path, new_content, updated_parent_documentation)

  def delete_documentation_for_file(self, file_path) -> None:
    """
    Delete documentation for the file.
    Used when the `change_type` of the file is `DELETED`.
    """
    file_docs_path = self.cache.get(file_path).generated_docs_path
    print(f"File deleted: {file_path}")
    print(f"Old file docs path: {file_docs_path}")
    if os.path.exists(file_docs_path):
      os.remove(file_docs_path)
      print(f"Deleted documentation for {file_path}")

  def get_changes(self, diff, main_branch_commit, curr_branch_commit):
    path = self.get_file_path(diff)
    old_content = git_utils.get_file_commit_content(self.root_folder, path, main_branch_commit)
    new_content = git_utils.get_file_commit_content(self.root_folder, path, curr_branch_commit)
    return ast_utils.get_function_changes(path, old_content, new_content)
  
  def get_parents_count(self, path, changes):
    filtered = ast_utils.filter_changes(changes)
    parent_dependencies = code2flow_utils.get_parent_dependencies(self.ast_agent.graph, filtered, path)
    return len(parent_dependencies)
  
  def get_file_path(self, diff):
    path = os.path.join(self.root_folder, diff.a_path)
    path = os.path.abspath(path)
    return path

  def _get_old_file_docs(self, file_path):
    cached_docs_path = self.cache.get(file_path).generated_docs_path
    return doc_utils.read_file_content(cached_docs_path)
  
  def _changes_to_string(self, changes):
    return '\n'.join([f'- {str(change)}' for change in changes])
  
  def _write_docs_and_cache(self, file_path, content, docs):
		# Write the updated documentation to the output directory
    updated_docs_path = doc_utils.write_file_docs(
      output_dir=self.output_folder,
      root_folder=self.root_folder,
      file_path=file_path,
      docs=docs
    )
    # Update the cache with the new documentation path and save it
    self.cache.update_docs(file_path, content, updated_docs_path)
    doc_utils.save_cache(self.output_folder, self.cache)