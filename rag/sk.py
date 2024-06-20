import asyncio
import ollama
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.ollama.services.ollama_chat_completion import OllamaChatCompletion
from semantic_kernel.connectors.ai.ollama.services.ollama_text_embedding import OllamaTextEmbedding
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.core_plugins.text_memory_plugin import TextMemoryPlugin
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory
from semantic_kernel.memory.volatile_memory_store import  VolatileMemoryStore
from semantic_kernel.memory.memory_store_base import MemoryStoreBase
from semantic_kernel.connectors.memory.azure_cognitive_search import AzureCognitiveSearchMemoryStore

kernel = Kernel()

# Add a chat completion service
ollama_chat_completion = OllamaChatCompletion(
  service_id="chat-completion",
  ai_model_id="llama3",
  url="http://localhost:11434/api/chat"
)
kernel.add_service(ollama_chat_completion)
# Add a text embedding service
embedding_generator = OllamaTextEmbedding(
  service_id="embedding",
  ai_model_id="all-minilm",
  url="http://localhost:11434/api/embed"
)
kernel.add_service(embedding_generator)

prompt = """
Who are you?
"""
embedding = ollama.embeddings(
  model='all-minilm',
  prompt='Llamas are members of the camelid family',
)

# Prompt configuration
prompt_template_config = PromptTemplateConfig(
  template=prompt,
  name="tldr",
  template_format="semantic-kernel",
)

# Add a function with the prompt config to the kernel
function = kernel.add_function(
  function_name="tldr_function",
  plugin_name="tldr_plugin",
  prompt_template_config=prompt_template_config,
)

# Register memory store using Azure AI Search 
ms = VolatileMemoryStore()
memory = SemanticTextMemory(storage=ms, embeddings_generator=embedding_generator)
kernel.add_plugin(TextMemoryPlugin(memory), "TextMemoryPluginACS")
print("------------------")
collection_id = "generic"
async def populate_memory(memory: SemanticTextMemory) -> None:
  # Add some documents to the semantic memory
  await ms.create_collection(collection_id)
  result = await memory.get_collections()
  print(result)
  result = await ms.get_nearest_matches(collection_name=collection_id, embedding=[embedding], limit=1)
  print(result)

async def main():
  result = await kernel.invoke(function)
  print(result)

if __name__ == "__main__":
  asyncio.run(populate_memory(memory))