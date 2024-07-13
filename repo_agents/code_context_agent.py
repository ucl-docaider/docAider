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
from plugins.code_context_plugin import CodeContextPlugin
from code2flow.code2flow import utils as graph_utils
from autogen_utils import utils as autogen_utils
from prompt import CODE_CONTEXT_PROMPT
from typing import Annotated
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

async def code_context_explainer() -> Annotated[str, "The code context description."]:
  # Initialize the kernel
  kernel = Kernel()
  output_folder = "./docs_output"
  file_path = "/Users/chengqike/Desktop/summer_project/repo-copilot/repo_agents/samples/data_processor.py"
  graph = graph_utils.get_call_graph(output_folder)

  # Add Azure OpenAI chat completion
  kernel.add_service(AzureChatCompletion(
    deployment_name=os.getenv("CHAT_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
  ))
  kernel.add_plugin(
    CodeContextPlugin(),
    plugin_name="CodeContext",
  )

  chat_completion : AzureChatCompletion = kernel.get_service(type=ChatCompletionClientBase)
  # Enable planning
  execution_settings = AzureChatPromptExecutionSettings(
    tool_choice="auto",
    temperature=0
  )
  execution_settings.function_call_behavior = FunctionCallBehavior.EnableFunctions(auto_invoke=True, filters={})
  # Create a history of the conversation
  history = ChatHistory()
  history.add_system_message(
    "Remember to ask for help if you're unsure how to proceed."
    "You are a helpful assistant who can provide the contextual description and explanation of Python code."
  )
  history.add_message({
    "role": "user",
    "content": CODE_CONTEXT_PROMPT.format(
        file_name=os.path.basename(file_path),
        info_of_called_functions=get_called_function(file_path, graph)
    )
  })
  # Get the response from the AI
  result = (await chat_completion.get_chat_message_contents(
    chat_history=history,
    settings=execution_settings,
    kernel=kernel,
    arguments=KernelArguments(),
  ))[0]
  return str(result)

def get_called_function(
  file_path: Annotated[str, "The file path"],
  graph: Annotated[str, "The function call graph"]
) -> Annotated[str, "The information of the called functions in the file"]:
  file_to_calls = graph_utils.get_file_to_functions(graph)
  calls = file_to_calls[file_path]
  bfs_explore = graph_utils.explore_call_graph(graph)
  info_of_called_functions = autogen_utils.get_additional_docs_calls(calls, graph, bfs_explore)
  return info_of_called_functions

if __name__ == "__main__":
  result = asyncio.run(code_context_explainer())
  print(result)