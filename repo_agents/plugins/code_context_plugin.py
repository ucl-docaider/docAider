import os
from repo_agents.ast_agent import ASTAgent
from semantic_kernel.functions import kernel_function
from typing import Annotated

class CodeContextPlugin:
  def __init__(self) -> None:
    self.ast_helper = ASTAgent()

  @kernel_function(
    name="get_file_content",
    description="Gets the content of a file"
  )
  def get_file_content(
    self,
    file_path: Annotated[str, "The file path"]
  ) -> Annotated[str, "The content of the file"]:
    with open(file_path, "r") as file:
      return file.read()
  
  @kernel_function(
    name="get_callee_function_info",
    description="Gets callee function info"
  )
  def get_callee_function_info(
    self,
    file_path: Annotated[str, "The file path"]
  ) -> Annotated[str, "The information of the callee functions"]:
    return self.ast_helper.get_callee_function_info(file_path)