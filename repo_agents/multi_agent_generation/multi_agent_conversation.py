import os
import asyncio
from autogen import ConversableAgent, register_function
import azure_openai_settings as ai_service_settings
from repo_agents.multi_agent_generation.code_context_agent import CodeContextAgent
from repo_agents.multi_agent_generation.prompt import DOCUMENTATION_PROMPT, REVIEWER_PROMPT, REVISOR_PROMPT
from repo_documentation.utils import Mode, save_prompt_debug, read_file_content
from typing import Annotated

"""
Multi-agent conversation pattern: sequential chats
Code context agent: provides description and explanation for code context (optional)
Documentation generation agent: generates documentation for the code
Review agent: checks the quality of generated documentation and provides improvement suggestions
Revise agent: Revises the documentation based on the reviewer's comments
Agent manager: is the mediator of the conversation
"""

root_folder = os.path.abspath(os.getenv("ROOT_FOLDER"))
output_folder = os.path.join(root_folder, "docs_output")
code_context_agent = CodeContextAgent()

documentation_generation_agent = ConversableAgent(
  name="documentation_generation_agent",
  system_message="You are an AI documentation assistant, and your task is to generate code level documentation documentation for the code.",
  llm_config=ai_service_settings.autogen_llm_config,
  human_input_mode="NEVER"
)

review_agent = ConversableAgent(
  name="documentation_reviewer",
  system_message="You are a documentation reviewer for code level documentation who can check the quality of the generated documentation and improve it.",
  llm_config=ai_service_settings.autogen_llm_config,
  human_input_mode="NEVER"
)

revise_agent = ConversableAgent(
  name="documentation_revisor",
  system_message="You are a documentation revisor who can revise the documentation based on the review agent's sugggestions",
  llm_config=ai_service_settings.autogen_llm_config,
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
  """
  This function calls the method `code_context_agent.code_context_explanation`.
  The purpose is to register the function to agents.
  This encapsulation is necessary because agents can only call functions, but not methods.
  """
  return asyncio.run(code_context_agent.code_context_explanation(file_path))

# Tool use: register functions to agents
register_function(
  code_context_explainer,
  caller=documentation_generation_agent,
  executor=agent_manager,
  name="code_context_explainer",
  description="Generates code context description",
)

def multi_agent_documentation_generation(file_path) -> str:
  file_content = read_file_content(file_path)

  chat_result = agent_manager.initiate_chats(
    [
      {
        "recipient": documentation_generation_agent,
        # Context: the prompt, including instructions and doc template,
        # Carryover: the output of the code context agent.
        "message": DOCUMENTATION_PROMPT.format(
          file_path=file_path,
          file_name=os.path.basename(file_path)
        ),
        "max_turns": 2,
        "summary_method": "last_msg",
      },
      {
        "recipient": review_agent,
        # Context: the source code,
        # Carryover: the output of the doc gen agent.
        "message": REVIEWER_PROMPT,
        "max_turns": 1,
        "summary_method": "last_msg",
      },
      {
        "recipient": revise_agent,
        # Context: None,
        # Carryover: the documentation.
        "message": REVISOR_PROMPT.format(file_content=file_content),
        "max_turns": 1,
        "summary_method": "last_msg",
      },
    ]
  )
  # Save prompt text for debug
  save_prompt_debug(output_folder, file_path + "_generation_agent", chat_result[0].chat_history[2]["content"], Mode.CREATE)
  save_prompt_debug(output_folder, file_path + "_reviewer_agent", chat_result[1].chat_history[0]["content"], Mode.CREATE)
  save_prompt_debug(output_folder, file_path + "_revisor_agent", chat_result[2].chat_history[0]["content"], Mode.CREATE)
  return chat_result[2].chat_history[-1]["content"]
