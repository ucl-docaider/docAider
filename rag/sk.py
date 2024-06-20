import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.ollama.services.ollama_chat_completion import OllamaChatCompletion
from semantic_kernel.connectors.ai.ollama.services.ollama_text_embedding import OllamaTextEmbedding
from semantic_kernel.prompt_template import PromptTemplateConfig

kernel = Kernel()

service_id = "chat-gpt"
# Add a chat completion service
kernel.add_service(
  service=OllamaChatCompletion(
    service_id=service_id,
    ai_model_id="llama3",
    url="http://localhost:11434/api/chat"
  )
)
# Add a text embedding service


prompt = """
Who are you?
"""

# Prompt configuration
prompt_template_config = PromptTemplateConfig(
  template=prompt,
  name="tldr",
  template_format="semantic-kernel",
)

# Register memory store using Azure AI Search 
# TODO

# Add a function with the prompt config to the kernel
function = kernel.add_function(
  function_name="tldr_function",
  plugin_name="tldr_plugin",
  prompt_template_config=prompt_template_config,
)

async def main():
  result = await kernel.invoke(function)
  print(result)

if __name__ == "__main__":
  asyncio.run(main())
