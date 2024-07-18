import asyncio, os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

import azure_openai_settings as ai_service_settings
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_call_behavior import FunctionCallBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.functions.kernel_arguments import KernelArguments
from repo_agents.plugins.code_context_plugin import CodeContextPlugin
from repo_agents.prompt import CODE_CONTEXT_PROMPT
from repo_documentation.utils import Mode, save_prompt_debug
from typing import Annotated

class CodeContextAgent:
  """
  This agent provides context explanation of code snippet.
  It is Self-contained, can be either included or excluded from the multi-agent conversation pattern.
  The purpose is to test whether the code context explanation increases the documentation quality.
  Additionally, as a lightweight code explainer, the user can consult with this agent for code context description.
  """
  def __init__(self) -> None:
    self.kernel = Kernel()

    # Add Azure OpenAI chat completion
    self.kernel.add_service(ai_service_settings.azure_chat_completion_service)

    self.chat_completion : AzureChatCompletion = self.kernel.get_service(type=ChatCompletionClientBase)
    # Enable planning
    self.execution_settings = AzureChatPromptExecutionSettings(
      tool_choice="auto",
      temperature=0
    )
    self.execution_settings.function_call_behavior = FunctionCallBehavior.EnableFunctions(auto_invoke=True, filters={})
    # Create a history of the conversation
    self.history = ChatHistory()
    self.history.add_system_message(
      "Remember to ask for help if you're unsure how to proceed."
      "You are a helpful assistant who can provide the contextual description and explanation of the code."
    )
    # Load the Github info plugin
    self.kernel.add_plugin(
      CodeContextPlugin(),
      plugin_name="CodeContext",
    )

  async def code_context_explanation(self, file_path) -> Annotated[str, "The code context description."]:
    """
    Returns the code context explanation of a source file.
    """
    message = CODE_CONTEXT_PROMPT.format(file_path=file_path)
    # Save prompt text for debug
    output_folder = os.path.join(os.getenv("ROOT_FOLDER"), "docs_output")
    save_prompt_debug(output_folder, file_path + "_code_context", message, Mode.UPDATE)
    
    self.history.add_message({
      "role": "user",
      "content": message,
    })
    # Get the response from the AI
    result = (await self.chat_completion.get_chat_message_contents(
      chat_history=self.history,
      settings=self.execution_settings,
      kernel=self.kernel,
      arguments=KernelArguments(),
    ))[0]
    return str(result)

# Test this agent
if __name__ == "__main__":
  cca = CodeContextAgent()
  file_path = "your-source-file-path."
  result = asyncio.run(cca.code_context_explanation(file_path))
  print(result)