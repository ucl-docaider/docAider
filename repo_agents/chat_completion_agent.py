import azure_openai_settings as ai_service_settings
from semantic_kernel import Kernel
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from exceptions import SemanticKernelError

class ChatCompletionAgent:
  def __init__(self) -> None:
    # Semantic kernel args
    self.kernel = Kernel()
    self.kernel.add_service(ai_service_settings.azure_chat_completion_service)
    self.execution_settings = AzureChatPromptExecutionSettings(
      temperature=0,  
    ) # Configure execution settings. You can TUNE PARAMETERS here.

  async def generate_response(self, prompt) -> str:
    """
    Generates LLM response for the given prompt.
    Ensure you have all environment variables set up correctly. Check `.env_example` file to find out what they are.
    Note: This is an async method, please use `asyncio.run()` in the caller function.
    """
    # Configure the prompt template
    prompt_template_config = PromptTemplateConfig(
      template=prompt,
      name="chat-completion",
      template_format="semantic-kernel",
      execution_settings=self.execution_settings
    )
    # Add summarization function to the kernel
    chat_completion = self.kernel.add_function(
      function_name="chat_completion",
      plugin_name="chat_completion",
      prompt_template_config=prompt_template_config,
    )

    response = ""
    try:
      response = str(await self.kernel.invoke(chat_completion))
    except:
      raise SemanticKernelError(f"The kernel failed to invoke the chat_completion function. Please check your Azure OpenAI service availability and try again.")
    return response