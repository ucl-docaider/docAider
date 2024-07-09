import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from semantic_kernel import Kernel
from rag.retriever import Retriever
from semantic_kernel.connectors.ai.ollama.services.ollama_chat_completion import OllamaChatCompletion
from semantic_kernel.connectors.ai.ollama.services.ollama_text_embedding import OllamaTextEmbedding
from semantic_kernel.connectors.ai.ollama.ollama_prompt_execution_settings import OllamaChatPromptExecutionSettings
from semantic_kernel.prompt_template import PromptTemplateConfig
from repo_documentation.prompt import DOCUMENTATION_PROMPT
from exceptions import SemanticKernelError

class DocumentationGenerator():
  """
  This class implements the RAG architecture for generating documentation for the code.
  It uses a retriever to get context information and uses a LLM-based generator to generate documentation.
  Semantic Kernel is central of the implementation.
  """
  def __init__(self, llm_id):
    """
    Initialize a new instance of the DocumentationGenerator class

    Args:
      llm_id: Ollama model name, see https://ollama.ai/library
    """
    self.llm_id = llm_id
    self.kernel = Kernel()
    self.context_retriever = Retriever(
      ai_search_api_key=os.getenv("AZURE_KEY_CREDENTIAL"),
      endpoint=os.getenv("SEARCH_ENDPOINT"),
      index_name="repo-index"
    )
    self.doc_retriever = Retriever(
      ai_search_api_key=os.getenv("AZURE_KEY_CREDENTIAL"),
      endpoint=os.getenv("SEARCH_ENDPOINT"),
      index_name="documentation-index"
    )
    self.chat_service_id = "documentation_generation"
    self.prompt = ""

    self._init()    
    print(f"Documentation generator initialised successfully.")

  def _init(self):
    """
    Initialse kernel services and retrievers
    """
    # Add a chat completion service
    ollama_chat_completion = OllamaChatCompletion(
      service_id=self.chat_service_id,
      ai_model_id=self.llm_id,
      url="http://localhost:11434/api/chat"
    )
    self.kernel.add_service(ollama_chat_completion)
    # Add a text embedding service
    embedding_generator = OllamaTextEmbedding(
      service_id="embedding",
      ai_model_id="all-minilm"
    )
    self.kernel.add_service(embedding_generator)

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
    execution_settings = OllamaChatPromptExecutionSettings(
      service_id=self.chat_service_id,
      ai_model_id=self.llm_id,
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
    print(f"Waiting for semantic kernel to respond...")
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