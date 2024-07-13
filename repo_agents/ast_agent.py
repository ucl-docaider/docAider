import os
from code2flow.code2flow import utils as graph_utils
from autogen_utils import utils as autogen_utils

class ASTAgent:
  def __init__(self, root_folder) -> None:
    graph_utils.generate_graph(root_folder, os.getenv("OUTPUT_FOLDER"))
    self.root_folder = root_folder
    self.graph = graph_utils.get_call_graph(os.getenv("OUTPUT_FOLDER"))
    self.file_to_calls = graph_utils.get_file_to_functions(self.graph)
    self.bfs_explore = graph_utils.explore_call_graph(self.graph)

  def get_callee_function_info(self, file_path) -> str:
    calls = self.file_to_calls[file_path]
    callee_function_info = autogen_utils.get_additional_docs_calls(calls, self.graph, self.bfs_explore)
    return callee_function_info