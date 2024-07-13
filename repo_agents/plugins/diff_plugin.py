from semantic_kernel.functions import kernel_function
from typing import Annotated
from difflib import Differ

class DiffPlugin:
  def __init__(self) -> None:
    pass

  @kernel_function(
    name="get_difference_of_two_files",
    description="Gets the difference of the two files"
  )
  def get_difference_of_two_files(
    file1: Annotated[str, "The first file path"],
    file2: Annotated[str, "The second file path"]
  ) -> Annotated[list, "The diff list"]:
    with open(file1) as file_1, open(file2) as file_2: 
      differ = Differ()
      diff_file = "".join(differ.compare(file_1.readlines(), file_2.readlines()))
    return diff_file
  
  res = get_difference_of_two_files(
    "/Users/chengqike/Desktop/summer_project/repo-copilot/repo_agents/samples/main.py",
    "/Users/chengqike/Desktop/summer_project/repo-copilot/repo_agents/samples/main2.py"
  )
  print(res)