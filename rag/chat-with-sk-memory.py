import asyncio
import ollama
import os
from semantic_kernel import Kernel
from semantic_kernel.functions import KernelFunction
from semantic_kernel.connectors.ai.ollama.services.ollama_chat_completion import OllamaChatCompletion
from semantic_kernel.connectors.ai.ollama.services.ollama_text_embedding import OllamaTextEmbedding
from semantic_kernel.prompt_template import InputVariable, PromptTemplateConfig
from semantic_kernel.core_plugins.text_memory_plugin import TextMemoryPlugin
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory
from semantic_kernel.memory.volatile_memory_store import  VolatileMemoryStore

kernel = Kernel()
collection_id = "generic"
chat_service_id = "chat-with-llm"

# Add a chat completion service
ollama_chat_completion = OllamaChatCompletion(
  service_id=chat_service_id,
  ai_model_id="llama3",
  url="http://localhost:11434/api/chat"
)
kernel.add_service(ollama_chat_completion)
# Add a text embedding service
embedding_generator = OllamaTextEmbedding(
  service_id="embedding",
  ai_model_id="all-minilm"
)
kernel.add_service(embedding_generator)

volatile_memory_store = VolatileMemoryStore() # Volatile memory store
# Register the memory store to the semantic text memory
memory = SemanticTextMemory(storage=volatile_memory_store, embeddings_generator=embedding_generator)
text_memory_plugin = TextMemoryPlugin(memory)
kernel.add_plugin(text_memory_plugin, "TextMemoryPluginVMS")

# Save information or knowledge to the memory
async def populate_memory(memory: SemanticTextMemory, id: str, text: str) -> None:
  await memory.save_information(collection=collection_id, id=id, text=text)

# set up a chat using the knowledge from memory
async def setup_chat_with_memory(kernel: Kernel, service_id: str) -> KernelFunction:
  prompt = """
  {{$input}}
  Generate a response beased on the user input above.
  This is the background information for you. You can use or not use it.
  {{$document}}
  You can say "I don't know" if you do not have an answer.
  """

  # Configure the prompt template
  prompt_template_config = PromptTemplateConfig(
    template=prompt,
    name="chat_with_memory",
    template_format="semantic-kernel",
    input_variables=[
      InputVariable(name="input", description="The user input", is_required=True),
      InputVariable(name="document",description="The retrieval document", is_required=True)
    ],
  )

  return kernel.add_function(
    function_name="chat_with_memory",
    plugin_name="RAG",
    prompt_template_config=prompt_template_config,
  )

# Perform the chat with LLM considering background knowledge (Basic RAG architecture)
async def rag_chat(user_input: str):
  print(f"Searching relevant document from the memory...")
  retrieval_document = (await memory.search(collection=collection_id, query=user_input))[0].text
  print(f"Retrieved document: {retrieval_document}")
  print(f"Setting up a chat function with memory...")
  chat_function = await setup_chat_with_memory(kernel, chat_service_id)
  print(f"Generating a response...")
  response = await kernel.invoke(chat_function, input=user_input, document=retrieval_document)
  print(f"User: {user_input}")
  print(f"LLM says: {response}")

# Search the memory to find a match
async def memory_search(memory: SemanticTextMemory, query: str):
  result = await memory.search(collection=collection_id, query=query)
  print(result[0].text)

# Main function of the module
async def main() -> None:
  # Inject some information samples to memory
  await populate_memory(memory=memory, id="id1", text="Sally's savings from 2023 are $50,000")
  await populate_memory(memory=memory, id="id2", text="Jack's savings from 2020 are $100,000")
  await populate_memory(memory=memory, id="id2", text="My savings from 2023 are $70,000")
  # Construct the user input
  user_input = "Do you know Sally's savings from 2023?"
  await rag_chat(user_input)

if __name__ == "__main__":
  asyncio.run(main())