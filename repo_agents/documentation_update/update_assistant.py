import asyncio
import repo_documentation.utils as doc_utils
from repo_agents.chat_completion_agent import ChatCompletionAgent
from repo_agents.documentation_update import git_utils
from repo_agents.prompt import DOCUMENTATION_PROMPT, DOCUMENTATION_UPDATE_PROMPT, PARENT_UPDATE, UPDATE_BY_COMMENT_PROMPT

class UpdateAssistant:
  def __init__(self, root_folder, output_folder, save_debug=False) -> None:
    self.root_folder = root_folder
    self.output_folder = output_folder
    self.chat_completion_agent = ChatCompletionAgent()
    self.cache = doc_utils.get_cache(self.output_folder)
    self.save_debug = save_debug

  def update_documentation_based_on_comment(self, file_path, comment, branch_latest_commit):
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

  def _get_old_file_docs(self, file_path):
    cached_docs_path = self.cache.get(file_path).generated_docs_path
    return doc_utils.read_file_content(cached_docs_path)
  
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