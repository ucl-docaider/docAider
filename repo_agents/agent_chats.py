import os, sys, asyncio, pprint
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from autogen import ConversableAgent, register_function
from autogen_utils import utils as autogen_utils
from rag.retriever import Retriever
from code2flow.code2flow import utils as graph_utils
from autogen_utils import config
from typing import Annotated, Literal
from code_context_agent import code_context_explainer
from doc_gen_agent import DocumentationGenerationAgent
from prompt import DOCUMENTATION_PROMPT

root_folder = "./samples"
output_dir = "./docs_output"
file_path = "/Users/chengqike/Desktop/summer_project/repo-copilot/repo_agents/samples/data_processor.py"

"""code_explainer = ConversableAgent(
  name="code_explainer",
  system_message="You are a helpful AI assistant. You can help with generating description and explanation for Python code.",
  llm_config=config.llm_config
)"""

documentation_generator = ConversableAgent(
  name="documentation_generator",
  system_message="You are an AI documentation assistant, and your task is to generate documentation for Python code.",
  llm_config=config.llm_config
)

"""review_agent = ConversableAgent(
  name="documentation_reviewer",
  system_message="You are a documentation reviewer who can check the quality of the generated documentation and improve it if necessary.",
  llm_config=config.llm_config
)"""

agent_manager = ConversableAgent(
  name="agent_manager",
  llm_config=False,
  human_input_mode="ALWAYS",
)

register_function(
  code_context_explainer,
  caller=documentation_generator,
  executor=agent_manager,
  name="code_context_explainer",
  description="Generates code context description",
)
"""
dg = DocumentationGenerationAgent()
def generate_documentation() -> Annotated[str, "The generated documentation for the Python file"]:
  return dg.generate_documentation_for_file(file_path)
register_function(
  generate_documentation,
  caller=documentation_generator,
  executor=agent_manager,
  name="documentation_generator",
  description="A function of generating documentation for Python file"
)"""

chat_result = agent_manager.initiate_chats(
  [
    {
      "recipient": documentation_generator,
      "message": DOCUMENTATION_PROMPT.format(file_name=os.path.basename(file_path)),
      "summary_method": "last_msg",
    },
  ]
)