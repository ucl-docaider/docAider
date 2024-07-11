import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.ollama.services.ollama_chat_completion import OllamaChatCompletion
from semantic_kernel.prompt_template import InputVariable, PromptTemplateConfig

# This plugin is a text-document summarizer

kernel = Kernel()

# Add a chat completion service
ollama_chat_completion = OllamaChatCompletion(
  service_id="chat-completion",
  ai_model_id="llama3",
  url="http://host.docker.internal:11434/api/chat"
)
kernel.add_service(ollama_chat_completion)

async def summarize(text_document: str) -> str:
  prompt = """{{$input}}
  Summarize the content above.
  """

  # Configure the prompt template
  prompt_template_config = PromptTemplateConfig(
    template=prompt,
    name="summarizer",
    template_format="semantic-kernel",
    input_variables=[
      InputVariable(name="input", description="The text document", is_required=True),
    ],
  )

  # Add summarization function to the kernel
  summarizer = kernel.add_function(
    function_name="summarizeFunc",
    plugin_name="summarizePlugin",
    prompt_template_config=prompt_template_config,
  )
  
  summary = await kernel.invoke(summarizer, input=text_document)
  print(summary)

# Test the summarizer
text_document = """
Cal and his best friend, Soy, learn that the frog (who prefers the name Deli) has sought them out for a reason. When a school administrator named Ream reveals himself to be a dragon, the boys discover that fairytales are real, and that there is magic afoot in Stagwood. With Ream on their tail, the trio must unearth a powerful tool protected by riddles and rile (the magic that fuels nightmares) to save the fate of all fairytales past. But, before Cal can defeat Ream, he has to deal with Soy's knack for arguing with magical creatures, discover the truth about Deli's identity, and earn his place as the hero of the story. The Guardians of Lore is a middle grade novel that centers around two life-long friends, infusing humor and fantasy-based riddles into a modern fairytale.
"""
asyncio.run(summarize(text_document))