import os
import repo_agents.multi_agent_generation.generation_conversation as gc
from repo_agents.ast_agent import ASTAgent
from semantic_kernel.functions import kernel_function
from cache.docs_cache import DocsCache
from repo_documentation.utils import save_cache, write_file_docs, read_file_content
from typing import Annotated

class DocumentationPlugin:
  def __init__(self) -> None:
    self.root_folder = os.path.abspath(os.getenv("ROOT_FOLDER"))
    self.output_folder = os.path.join(self.root_folder, "docs_output")
    self.ast_agent = ASTAgent()
    self.cache = DocsCache()

  @kernel_function(
    name="generate_documentation_for_file",
    description="Generates documentation for a file"
  )
  def generate_documentation_for_file(
    self,
    file_path: Annotated[str, "The file path"]
  ) -> None:
    """
    Generates documentation for a file.
    """
    file_content = read_file_content(file_path)
    documentation = gc.multi_agent_documentation_generation(file_path)
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
  def generate_all(self) -> None:
    """
    Generates documentation for all files under the root folder.
    """
    file_and_callee_function_dict = self.ast_agent.get_file_call_dict()
    
    for file_path, callee_functions in file_and_callee_function_dict.items():
      if file_path == 'EXTERNAL':  # Skip all external functions
        continue

      self.generate_documentation_for_file(file_path)
    
    save_cache(self.output_folder, self.cache)