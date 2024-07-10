import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from dotenv import load_dotenv
from semantic_kernel import Kernel
from rag.retriever import Retriever
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.prompt_template import PromptTemplateConfig
from repo_documentation.prompt import DOCUMENTATION_PROMPT
from exceptions import SemanticKernelError

load_dotenv(dotenv_path="../.env")

class DocumentationGenerator():
  """
  This class implements the RAG architecture for generating documentation for the code.
  It uses a retriever to get context information and uses a LLM-based generator to generate documentation.
  Semantic Kernel is central of the implementation.
  """
  def __init__(self):
    """
    Initialize a new instance of the DocumentationGenerator class
    """
    self.kernel = Kernel()
    self.context_retriever = Retriever(
      ai_search_api_key=os.getenv("AZURE_AI_SEARCH_KEY"),
      endpoint=os.getenv("SEARCH_ENDPOINT"),
      index_name="repo-index"
    )
    self.doc_retriever = Retriever(
      ai_search_api_key=os.getenv("AZURE_AI_SEARCH_KEY"),
      endpoint=os.getenv("SEARCH_ENDPOINT"),
      index_name="documentation-index"
    )
    self.chat_service_id = "documentation_generation"
    self.prompt = ""

    self._init()

  def _init(self):
    """
    Initialse kernel services and retrievers
    """
    # Add a chat completion service
    azure_open_ai_completion = AzureChatCompletion(
      service_id=self.chat_service_id,
      deployment_name=os.getenv("CHAT_DEPLOYMENT_NAME"),
      api_key=os.getenv("AZURE_OPENAI_API_KEY"),
      endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
      api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    self.kernel.add_service(azure_open_ai_completion)

    if not self.context_retriever.index_exist_or_not():
      self.context_retriever.create_index(self.context_retriever.index_name)
    if not self.doc_retriever.index_exist_or_not():
      self.doc_retriever.create_index(self.doc_retriever.index_name)

  async def generate_documentation(self, file_path, file_content, root_folder, additional_docs) -> str:
    """
    This is a plugin function, which generates documentation for code.

    Args:
      file_path: the name of the source file.
      file_content: the source code.
      root_folder: the root folder of the repository.
      additional_docs: the additional docs.
    
    Returns:
      LLM-generated documentation in string
    """

    file_name = os.path.basename(file_path)
    prompt = DOCUMENTATION_PROMPT.format(
      file_name=file_name,
      file_content=file_content,
      root_folder=root_folder,
      additional_docs=additional_docs
    )
    self.prompt = prompt

    # Configure execution settings
    execution_settings = AzureChatPromptExecutionSettings(
      service_id=self.chat_service_id,
      temperature=0      
    )

    # Configure the prompt template
    prompt_template_config = PromptTemplateConfig(
      template=prompt,
      name="documentation-generation",
      template_format="semantic-kernel",
      execution_settings=execution_settings
    )

    # Add summarization function to the kernel
    documentation_generator = self.kernel.add_function(
      function_name="documentation_generation",
      plugin_name="documentation_generator",
      prompt_template_config=prompt_template_config,
    )

    # Invoke kernel to generate documentation
    try:
      documentation = str(await self.kernel.invoke(documentation_generator))
      # Save documentation to the database
      """self.doc_retriever.upsert_documents([{
        "id": str(self.doc_retriever.search_client.get_document_count()),
        "filePath": file_path,
        "content": documentation,
        "comments": "" # set to be empty string temporarily
      }])"""
      print(f"Documentation generated for {file_name}.")
      return documentation
    except:
      raise SemanticKernelError(f"The generation for {file_name} failed. Please check kernel configurations and try again.")