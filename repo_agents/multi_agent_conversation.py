import os, sys, asyncio, pprint
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from autogen import ConversableAgent, register_function
from autogen_utils import config
from code_context_agent import CodeContextAgent
from prompt import DOCUMENTATION_PROMPT
from typing import Annotated

code_context_agent = CodeContextAgent()
documentation_generation_agent = ConversableAgent(
  name="documentation_generation_agent",
  system_message="You are an AI documentation assistant, and your task is to generate documentation for Python code.",
  llm_config=config.llm_config,
  human_input_mode="NEVER"
)
review_agent = ConversableAgent(
  name="documentation_reviewer",
  system_message="You are a documentation reviewer who can check the quality of the generated documentation and improve it if necessary.",
  llm_config=config.llm_config,
  human_input_mode="NEVER"
)
agent_manager = ConversableAgent(
  name="agent_manager",
  llm_config=False,
  human_input_mode="NEVER"
)

def code_context_explainer(
  file_path: Annotated[str, "The file path"]
) -> Annotated[str, "The code context description"]:
  return asyncio.run(code_context_agent.code_context_explanation(file_path))

register_function(
  code_context_explainer,
  caller=documentation_generation_agent,
  executor=agent_manager,
  name="code_context_explainer",
  description="Generates code context description",
)

def multi_agent_documentation_generation(file_path) -> str:
  chat_result = agent_manager.initiate_chats(
    [
      {
        "recipient": documentation_generation_agent,
        "message": DOCUMENTATION_PROMPT.format(file_path=file_path),
        "max_turns": 2,
        "summary_method": "last_msg",
      },
      {
        "recipient": review_agent,
        "message": "This is the generated documentation for the source code. Please review it and improve the documentation quality.",
        "max_turns": 1,
        "summary_method": "reflection_with_llm",
      }
    ]
  )
  return chat_result[1].chat_history[-1]["content"]

#result = multi_agent_documentation_generation("/Users/chengqike/Desktop/summer_project/repo-copilot/repo_agents/samples/data_processor.py")
#print(result)