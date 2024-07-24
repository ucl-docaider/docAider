import os, asyncio
from repo_agents.chat_completion_agent import ChatCompletionAgent
from repo_agents.prompt import DOCUMENTATION_PROMPT
from repo_agents.ast_agent import ASTAgent
from cache.docs_cache import DocsCache
from repo_documentation import utils as doc_utils

class DocumentationAgent:
  """
  This agent generates documentation for file(s).
  The caller file is the `repo_documentation/app.py`, which is the entry point for execution.
  """
  def __init__(self, save_debug=False) -> None:
    self.root_folder = os.path.abspath(os.getenv("ROOT_FOLDER"))
    self.output_folder = os.path.join(self.root_folder, "docs_output")
    self.ast_agent = ASTAgent()
    self.cache = DocsCache()
    self.chat_completion_agent = ChatCompletionAgent()
    self.save_debug = save_debug

  def generate_documentation_for_file(self, file_path) -> None:
    """
    Generate documentation for a file using LLM and save to the output folder.
    """
    file_name = os.path.basename(file_path)
    file_content = doc_utils.read_file_content(file_path)
    callee_functions = self.ast_agent.get_callee_function_info(file_path)
    prompt = DOCUMENTATION_PROMPT.format(
      file_name=file_name,
      file_content=file_content,
      callee_functions=callee_functions
    )

    documentation = asyncio.run(self.chat_completion_agent.generate_response(prompt))
    # Save the documentation
    output_path = doc_utils.write_file_docs(
      self.output_folder,
      self.root_folder,
      file_path,
      documentation
    )
    # Save the cache
    self.cache.add(file_path, file_content, output_path)

    # Save the prompt message for debug
    if self.save_debug:
      doc_utils.save_prompt_debug(self.output_folder, file_path, prompt, doc_utils.Mode.CREATE)
  
  def generate_all_documentation(self) -> None:
    """
    Generates documentation for all files under the root folder.
    """
    file_and_callee_function_dict = self.ast_agent.get_file_call_dict()
    
    for file_path, callee_functions in file_and_callee_function_dict.items():
      if file_path == 'EXTERNAL':  # Skip all external functions
        continue
      # Generate documentation for the file
      asyncio.run(self.generate_documentation_for_file(file_path, save_debug=True))
    # Save cache
    doc_utils.save_cache(self.output_folder, self.cache)