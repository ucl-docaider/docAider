import sys, os
from dotenv import load_dotenv
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from semantic_kernel import Kernel
from retriever import Retriever
from semantic_kernel.connectors.ai.ollama.services.ollama_chat_completion import OllamaChatCompletion
from semantic_kernel.connectors.ai.ollama.services.ollama_text_embedding import OllamaTextEmbedding
from semantic_kernel.prompt_template import PromptTemplateConfig
from repo_documentation.prompt import DOCUMENTATION_PROMPT

load_dotenv(dotenv_path='.env_rag')

class DocumentationGenerator():
  """
  This class provides functions of generating documentation.
  """
  def __init__(self):
    self.kernel = Kernel()
    self.retriever = Retriever(
      ai_search_api_key=os.getenv("AZURE_KEY_CREDENTIAL"),
      endpoint=os.getenv("SEARCH_ENDPOINT"),
      index_name="code-index"
    )
    self.chat_service_id = "documentation-generation"

    # Add a chat completion service
    ollama_chat_completion = OllamaChatCompletion(
      service_id=self.chat_service_id,
      ai_model_id="mistral",
      url="http://localhost:11434/api/chat"
    )
    self.kernel.add_service(ollama_chat_completion)

    # Add a text embedding service
    embedding_generator = OllamaTextEmbedding(
      service_id="embedding",
      ai_model_id="all-minilm"
    )
    self.kernel.add_service(embedding_generator)

  async def generate_documentation(self, file_name, file_content, root_folder, additional_docs) -> str:
    """
    This is a plugin function, which generates documentation for code.

    Args:
      file_name: the name of the source file.
      file_content: the source code
      root_folder: the root folder of the repository
      additional_docs: the additional docs
    
    Returns:
      LLM-generated documentation in string
    """
    prompt = DOCUMENTATION_PROMPT.format(
      file_name=file_name,
      file_content=file_content,
      root_folder=root_folder,
      additional_docs=additional_docs
    )

    # Configure the prompt template
    prompt_template_config = PromptTemplateConfig(
      template=prompt,
      name="documentation-generation",
      template_format="semantic-kernel",
    )

    # Add summarization function to the kernel
    documentation_generator = self.kernel.add_function(
      function_name="documentation_generation",
      plugin_name="documentation_generator",
      prompt_template_config=prompt_template_config,
    )
  
    documentation = await self.kernel.invoke(documentation_generator)
    return str(documentation)