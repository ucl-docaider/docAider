import os
import repo_agents.multi_agent_conversation as mac
from repo_agents.ast_agent import ASTAgent
from semantic_kernel.functions import kernel_function
from cache.docs_cache import DocsCache
from repo_documentation.utils import save_cache, write_file_docs
from typing import Annotated

class DocumentationPlugin:
  def __init__(self) -> None:
    self.root_folder = os.path.abspath(os.getenv("ROOT_FOLDER"))
    self.output_folder = os.path.join(self.root_folder, "docs_output")
    self.ast_helper = ASTAgent()
    self.cache = DocsCache()

  @kernel_function(
    name="generate_documentation_for_file",
    description="Generates documentation for a file"
  )
  def generate_documentation_for_file(
    self,
    file_path: Annotated[str, "The file path"]
  ) -> Annotated[str, "The documentation storage path"]:
    """
    Generates documentation for a file.
    """
    file_content = self.get_file_content(file_path)
    documentation = mac.multi_agent_documentation_generation(file_path)
    output_path = write_file_docs(
      self.output_folder,
      self.root_folder,
      file_path,
      documentation
    )
    self.cache.add(file_path, file_content, output_path)

  @kernel_function(
    name="generate_all_documentation",
    description="Generates documentation for all files under the root folder"
  )
  def generate_all(self):
    """
    Generates documentation for all files under the root folder.
    """
    file_and_callee_function_dict = self.ast_helper.get_file_call_dict()
    
    for file_path, callee_functions in file_and_callee_function_dict.items():
      if file_path == 'EXTERNAL':  # Skip all external functions
        continue

      self.generate_documentation_for_file(file_path)
    
    save_cache(self.output_folder, self.cache)

  def get_file_content(self, file_path) -> str:
    with open(file_path, "r") as file:
      return file.read()