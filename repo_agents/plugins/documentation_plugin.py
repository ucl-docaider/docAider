import os
import repo_agents.multi_agent_conversation as mac
from repo_agents.ast_agent import ASTAgent
from semantic_kernel.functions import kernel_function
from cache.docs_cache import DocsCache
from repo_documentation.utils import save_cache
from typing import Annotated

class DocumentationPlugin:
  def __init__(self, output_folder="./docs_output") -> None:
    self.output_folder = output_folder
    self.ast_helper = ASTAgent(os.getenv("ROOT_FOLDER"))
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
    output_path = self.save_documentation(
      os.path.basename(file_path),
      documentation=documentation
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

  def save_documentation(self, file_name, documentation, output_folder="./docs_output") -> str:
    """
    Saves the generated documentation to the output folder.
    """
    doc_file_name = file_name + ".md"
    path = os.path.join(output_folder, doc_file_name)
    with open(path, "w") as file:
      file.write(documentation)
    print(f"{doc_file_name} saved to {path}.")
    return path