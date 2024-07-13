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
from plugins.github_info_plugin import GithubInfoPlugin
from plugins.documentation_plugin import DocumentationPlugin
from typing import Annotated
from azure_openai_settings import azure_chat_completion_service
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

class GitRepoAgent:
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
      "You are a helpful repository copilot."
    )
    # Add plugins to the kernel
    self.kernel.add_plugin(
      GithubInfoPlugin(),
      plugin_name="github_info_plugin",
    )
    self.kernel.add_plugin(
      DocumentationPlugin(),
      plugin_name="documentation_plugin"
    )

  async def chat_with_agent(self, message) -> Annotated[str, "AI agent response"]:
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
    print("Assistant > " + str(result))
    self.history.add_message(result)
  
# Test this agent
# Note: nested async functions are problematic. (code_context_explanation is never awaited)
if __name__ == "__main__":
  copilot = GitRepoAgent()
  dg = DocumentationPlugin()
  print("Hello! I am your Github repo copilot.")
  print("Due to current AST analysis performs locally, we do not support relative paths.")
  print("Instead, you need to provide the absolute path of your file.")
  print("Note: the `samples` folder has the files for testing purpose.")
  print("I can help you find Github information, for example, you can ask: Show me the content of the file XXX in the repo XXX")
  print("See my plugin file to find out what functions I can do.")
  print("To terminate this conversation, you can say 'exit'.")
  while True:
    user_input = input("User > ")
    if user_input == "exit":
      break
    asyncio.run(copilot.chat_with_agent(user_input))

  file_path = input("Please enter the file path for which you want to generate documentation: ")
  result = dg.generate_documentation_for_file(file_path=file_path)
  print(result)