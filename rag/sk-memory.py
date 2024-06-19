import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai.services.azure_text_embedding import AzureTextEmbedding
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.core_plugins.text_memory_plugin import TextMemoryPlugin
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory
from semantic_kernel.memory.volatile_memory_store import VolatileMemoryStore
from semantic_kernel.connectors.memory.azure_cognitive_search import AzureCognitiveSearchMemoryStore

kernel = Kernel() # initialise a kernel instance

embedding_generator = AzureTextEmbedding(
  service_id="embedding",
)
kernel.add_service(embedding_generator) # add an embedding generation service to the kernel

# connect to an existing Azure AI Search service that we will use 
# as an external Vector Database to store and retrieve embeddings.
acs_memory_store = AzureCognitiveSearchMemoryStore(
  vector_size=1536,
  admin_key=os.environ["AZURE_KEY_CREDENTIAL"], # Azure AI Search API Key
  search_endpoint=os.environ["SEARCH_ENDPOINT"] # Azure AI Search End Point
)

# Create a memory that links to the Azure AI Search
memory = SemanticTextMemory(storage=acs_memory_store, embeddings_generator=embedding_generator)
# Add the memory plugin to the kernel
kernel.add_plugin(TextMemoryPlugin(memory), "TextMemoryPluginACS")

# Wuery the memory 
memory.search(query="I need a code snippet that added three numbers")

# Use `VolatileMemoryStore` instead of Azure AI Search Memory Store
"""
kernel = Kernel()

chat_service_id = "chat"

azure_chat_service = AzureChatCompletion(
  service_id=chat_service_id,
)
# next line assumes embeddings deployment name is "text-embedding", adjust the deployment name to the value of your chat model if needed
embedding_gen = AzureTextEmbedding(
  service_id="embedding",
)
kernel.add_service(azure_chat_service)
kernel.add_service(embedding_gen)

memory = SemanticTextMemory(storage=VolatileMemoryStore(), embeddings_generator=embedding_gen)
kernel.add_plugin(TextMemoryPlugin(memory), "TextMemoryPlugin")

collection_id = "generic"
memory.save_information(collection=collection_id, id="info1", text="Your budget for 2024 is $100,000")
memory.save_information(collection=collection_id, id="info2", text="Your savings from 2023 are $50,000")
memory.save_information(collection=collection_id, id="info3", text="Your investments are $80,000")

result = memory.search(collection_id, "What is my budget for 2024?")
print(result)"""