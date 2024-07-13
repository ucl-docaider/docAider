import sys, time, os, asyncio
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from rag.retriever import Retriever
from code2flow.code2flow import utils as graph_utils
from autogen_utils import utils as autogen_utils
from repo_documentation import utils as doc_utils
from cache.docs_cache import DocsCache
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.prompt_template import PromptTemplateConfig
from exceptions import DocGenByKernelFailed
from service_settings import azure_open_ai_chat_completion_service
from prompt import DOCUMENTATION_PROMPT

class DocumentationGenerationAgent:
  """
  This agent generates documentation for source files.
  """
  def __init__(self) -> None:
    self.kernel = Kernel()
    self._init()

  def _init(self):
    """
    Initialise kernel services and retrievers
    """
    # Add a chat completion service
    azure_open_ai_completion = AzureChatCompletion(
      deployment_name=os.getenv("CHAT_DEPLOYMENT_NAME"),
      api_key=os.getenv("AZURE_OPENAI_API_KEY"),
      endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
      api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    self.kernel.add_service(azure_open_ai_completion)

  def generate_documentation_for_file(self, file_path) -> str:
    file_name = os.path.basename(file_path)
    # Build the prompt message
    prompt = DOCUMENTATION_PROMPT.format(
      file_name=file_name,
    )
    # Configure execution settings
    execution_settings = AzureChatPromptExecutionSettings(
      temperature=0      
    )
    # Configure the prompt template
    prompt_template_config = PromptTemplateConfig(
      template=prompt,
      name="documentation-generation",
      template_format="semantic-kernel",
      execution_settings=execution_settings
    )
    # Add generation function to the kernel
    documentation_generator = self.kernel.add_function(
      function_name="documentation_generation",
      plugin_name="documentation_generator",
      prompt_template_config=prompt_template_config,
    )

    try:
      documentation = str(asyncio.run(self.kernel.invoke(documentation_generator)))
    except:
      raise DocGenByKernelFailed(f"Something went wrong when generating documentation for {file_name}.")

    return documentation

  """def generate_all(self) -> None:
    start_time = time.time()
    # 1. Generate graph
    graph_utils.generate_graph(self.root_folder, self.output_dir)
    graph = graph_utils.get_call_graph(self.output_dir)
    # 2. Build mapping of a file to the functions called within them
    file_to_calls = graph_utils.get_file_to_functions(graph)
    # 3. Build BFS exploration of the call graph
    bfs_explore = graph_utils.explore_call_graph(graph)
    # 4. Prepare cache, where we will map file paths to their respective documentation
    cache = DocsCache()
    # 5. Generate documentation for each file
    for file_path, calls in file_to_calls.items():
      if file_path == 'EXTERNAL':  # Skip all external functions
        continue

      file_name = os.path.basename(file_path)
      file_content = asyncio.run(self.file_retriever.search(query=f"{file_name}"))
      additional_docs = autogen_utils.get_additional_docs_calls(calls, graph, bfs_explore)
      documentation = asyncio.run(self.generate_documentation_for_file(file_path, additional_docs))
      # Write the documentation to a file
      docs_filepath = doc_utils.write_file_docs(
        output_dir=self.output_dir,
        root_folder=self.root_folder,
        file_path=file_path,
        docs=documentation
      )
      # 6. Add the file path and its according documentation to the cache
      cache.add(file_path, file_content, docs_filepath)
    # 7. Save cache to a file
    doc_utils.save_cache(self.output_dir, cache)
    total = round(time.time() - start_time, 3)
    print(f'Generated documentation ({cache.size()} files) can be found in {self.output_dir}')
    print(f"Documentation generation completed in {total}s.")
"""