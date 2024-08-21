import os
from code2flow.code2flow import utils as code2flow_utils

class ASTAgent:
  """
  This agent performs Abstract Syntax Tree (AST) analysis and generates a call graph of files.
  """
  def __init__(self) -> None:
    self.root_folder = os.path.abspath(os.getenv("ROOT_FOLDER"))
    self.output_folder = os.path.join(self.root_folder, "docs_output")
    code2flow_utils.generate_graph(self.root_folder, self.output_folder)
    self.graph = code2flow_utils.get_call_graph(self.output_folder)
    self.file_to_calls = code2flow_utils.get_file_to_functions(self.graph)
    self.bfs_explore = code2flow_utils.explore_call_graph(self.graph)

  def get_callee_function_info(self, file_path) -> str:
    """
    Returns callee functions in a file
    """
    calls = self.file_to_calls[file_path]
    callee_function_info = self.get_additional_docs_calls(calls)
    return callee_function_info
  
  def get_file_call_dict(self) -> dict:
    """
    Returns a dict mapping: (file, callee functions)
    """
    return self.file_to_calls
  
  def get_additional_docs_path(self, file_path):
    additional_docs = ""
    if file_path in self.file_to_calls:
      calls = self.file_to_calls[file_path]
      additional_docs += self.get_additional_docs_calls(calls)
    return additional_docs
  
  def get_additional_docs_calls(self, calls, max_depth=5):
    additional_docs = ""
    processed_callees = set()

    for call_name in calls:
      call = self.graph[call_name]
      if 'EXTERNAL' in call['file_name']:
        continue
      queue = [(call_name, 0)]
      visited = set()

      while queue:
        current_call, depth = queue.pop(0)
        if depth > max_depth:
          continue
        if current_call in visited:
          continue
        visited.add(current_call)

        caller_file = self.graph[current_call]['file_name']

        for callee in self.bfs_explore.get(current_call, []):
          callee_call = self.graph[callee]
          callee_file = callee_call['file_name']

          if 'EXTERNAL' not in callee_file and callee not in processed_callees and caller_file != callee_file:
            additional_docs += f"\nFunction/Class {callee_call['name']}:\n{callee_call['content']}\n"
            processed_callees.add(callee)
          if depth < max_depth and callee not in visited:
            queue.append((callee, depth + 1))
    return additional_docs