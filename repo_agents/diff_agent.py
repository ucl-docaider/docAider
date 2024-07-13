import asyncio, os

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_call_behavior import FunctionCallBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.functions.kernel_arguments import KernelArguments
from plugins.diff_plugin import DiffPlugin

async def main():
  # Initialize the kernel
  kernel = Kernel()

  # Add Azure OpenAI chat completion
  kernel.add_service(AzureChatCompletion(
    deployment_name=os.getenv("CHAT_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
  ))

  kernel.add_plugin(
    DiffPlugin(),
    plugin_name="Diff",
  )

  chat_completion : AzureChatCompletion = kernel.get_service(type=ChatCompletionClientBase)

  # Enable planning
  execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
  execution_settings.function_call_behavior = FunctionCallBehavior.EnableFunctions(auto_invoke=True, filters={})

  res = DiffPlugin.get_difference_of_two_files(
    "/Users/chengqike/Desktop/summer_project/repo-copilot/repo_agents/samples/main.py",
    "/Users/chengqike/Desktop/summer_project/repo-copilot/repo_agents/samples/main2.py"
  )

  # Create a history of the conversation
  history = ChatHistory()
  history.add_system_message("Remember to ask for help if you're unsure how to proceed.")
  history.add_message({
    "role": "user",
    "content": f"According to this Diff file: {res}, the changed line happends in which function, in which file and what is the change type in the following format: 'function name, file, change description, change type'"
  })

  # Get the response from the AI
  result = (await chat_completion.get_chat_message_contents(
    chat_history=history,
    settings=execution_settings,
    kernel=kernel,
    arguments=KernelArguments(),
  ))[0]

  # Print the results
  print("Assistant > " + str(result))

  # Add the message from the agent to the chat history
  history.add_message({
    "role": "assistant",
    "content": str(result)
  })

def get_file_content(file):
   with open(file, "r") as f:
      return f.read()

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())