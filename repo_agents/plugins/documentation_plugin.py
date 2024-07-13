import os
import multi_agent_conversation as mac
from semantic_kernel.functions import kernel_function
from typing import Annotated

class DocumentationPlugin:
  @kernel_function(
    name="generate_documentation_for_file",
    description="Generates documentation for a file"
  )
  def generate_documentation_for_file(
    self,
    file_path: Annotated[str, "The file path"]
  ) -> Annotated[str, "The documentation storage path"]:
    documentation = mac.multi_agent_documentation_generation(file_path)
    output_path = self.save_documentation(
      os.path.basename(file_path),
      documentation=documentation
    )
    return output_path

  # TODO: generate all docs
  def generate_all(self):
    pass

  def save_documentation(self, file_name, documentation) -> str:
    output_folder = os.getenv("OUTPUT_FOLDER")
    path = os.path.join(output_folder, file_name)
    with open(path, 'w') as file:
      file.write(documentation)
    return f"{file_name} saved to {path}."