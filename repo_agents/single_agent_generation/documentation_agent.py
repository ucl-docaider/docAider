import os, asyncio
import azure_openai_settings as ai_service_settings
from semantic_kernel import Kernel
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from repo_agents.single_agent_generation.prompt import DOCUMENTATION_PROMPT
from repo_agents.ast_agent import ASTAgent
from cache.docs_cache import DocsCache
from repo_documentation import utils as doc_utils
from exceptions import SemanticKernelError

class DocumentationAgent:
  """
  This agent generates documentation for file(s).
  The caller file is the `repo_documentation/app.py`, which is the entry point for execution.
  """
  def __init__(self) -> None:
    self.root_folder = os.path.abspath(os.getenv("ROOT_FOLDER"))
    self.output_folder = os.path.join(self.root_folder, "docs_output")
    self.ast_agent = ASTAgent()
    self.cache = DocsCache()
    # Semantic kernel args
    self.kernel = Kernel()
    self.kernel.add_service(ai_service_settings.azure_chat_completion_service)
    self.execution_settings = AzureChatPromptExecutionSettings(
      temperature=0,  
    ) # Configure execution settings. You can TUNE PARAMETERS here.

  async def generate_documentation_for_file(self, file_path, save_debug=False) -> None:
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

    # Configure the prompt template
    prompt_template_config = PromptTemplateConfig(
      template=prompt,
      name="documentation-generation",
      template_format="semantic-kernel",
      execution_settings=self.execution_settings
    )
    # Add summarization function to the kernel
    documentation_generator = self.kernel.add_function(
      function_name="documentation_generation",
      plugin_name="documentation_generator",
      prompt_template_config=prompt_template_config,
    )

    # Invoke kernel to generate documentation
    documentation = ""
    try:
      documentation = str(await self.kernel.invoke(documentation_generator))
    except:
      raise SemanticKernelError(f"The generation for {file_name} failed. Please check kernel configurations and try again.")

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
    if save_debug:
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