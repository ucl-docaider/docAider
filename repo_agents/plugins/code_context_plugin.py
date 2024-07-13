import os, sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(root_dir)
from rag.retriever import Retriever
from semantic_kernel.functions import kernel_function
from typing import Annotated

class CodeContextPlugin:
  def __init__(self) -> None:
    self.file_retriever = Retriever(
      ai_search_api_key=os.getenv("AZURE_AI_SEARCH_KEY"),
      endpoint=os.getenv("SEARCH_ENDPOINT"),
      index_name="repo-index"
    )

  @kernel_function(
    name="get_file_content",
    description="Gets the content of a file"
  )
  async def get_file_content(
    self,
    file_name: Annotated[str, "The file name"]
  ) -> Annotated[str, "The content of the file"]:
    return await self.file_retriever.search(query=f"{file_name}")