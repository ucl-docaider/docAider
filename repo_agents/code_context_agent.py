import asyncio, os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_call_behavior import FunctionCallBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.functions.kernel_arguments import KernelArguments
from plugins.code_context_plugin import CodeContextPlugin
from prompt import CODE_CONTEXT_PROMPT
from typing import Annotated
from azure_openai_settings import azure_chat_completion_service
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

class CodeContextAgent:
  def __init__(self) -> None:
    self.kernel = Kernel()

    # Add Azure OpenAI chat completion
    self.kernel.add_service(azure_chat_completion_service)

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
      "You are a helpful assistant who can provide the contextual description and explanation of Python code."
    )
    # Load the Github info plugin
    self.kernel.add_plugin(
      CodeContextPlugin(),
      plugin_name="CodeContext",
    )

  async def code_context_explanation(self, file_path) -> Annotated[str, "The code context description."]:
    message = CODE_CONTEXT_PROMPT.format(
      file_name=os.path.basename(file_path),
      file_path=file_path
    )
    
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
  file_path = "/Users/chengqike/Desktop/summer_project/repo-copilot/repo_agents/samples/data_processor.py"
  result = asyncio.run(cca.code_context_explanation(file_path))
  print(result)