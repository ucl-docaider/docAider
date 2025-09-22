import os
import asyncio
from typing import Annotated

from autogen import UserProxyAgent, ConversableAgent, register_function
import gemini_settings as ai_service_settings
from google.genai.errors import ServerError

from repo_documentation.prompt import DOCUMENTATION_PROMPT, \
    DOCUMENTATION_UPDATE_PROMPT, USR_PROMPT, PARENT_UPDATE, COMENT_UPDATE
from repo_documentation import utils
from repo_documentation.utils import Mode, save_prompt_debug, read_file_content
from autogen_utils.utils import load_assistant_agent, initiate_chat

from repo_agents.multi_agent_generation.code_context_agent import CodeContextAgent
from repo_agents.multi_agent_generation.prompt import DOCUMENTATION_PROMPT as MULTI_AGENT_DOC_PROMPT
from repo_agents.multi_agent_generation.prompt import REVIEWER_PROMPT, REVISOR_PROMPT

from .app import app


@app.task(autoretry_for=(ServerError,), retry_kwargs={'max_retries': 5}, retry_backoff=True)
def get_documentation(file_path,
                      file_content,
                      additional_docs,
                      output_dir,
                      root_folder,
                      save_debug=False):
    """
    Retrieves documentation for a given file.
    """
    assistant = load_assistant_agent()
    user = UserProxyAgent(name="user", code_execution_config=False)

    prompt_message = DOCUMENTATION_PROMPT.format(
        root_folder=root_folder,
        file_name=os.path.basename(file_path),
        file_content=file_content,
        additional_docs=additional_docs
    )

    initiate_chat(user, assistant, prompt_message)

    clean_out = assistant.last_message()['content'].replace('```html', '').replace('```', '').strip()

    if save_debug:
        utils.save_prompt_debug(
            output_dir, file_path, prompt_message, utils.Mode.CREATE)
        utils.save_response_debug(
            output_dir, file_path, clean_out, utils.Mode.CREATE)
    return clean_out


@app.task(autoretry_for=(ServerError,), retry_kwargs={'max_retries': 5}, retry_backoff=True)
def get_updated_documentation(file_path,
                             old_file_docs,
                             old_file_content,
                             new_file_content,
                             diff,
                             additional_docs,
                             changes,
                             output_dir,
                             save_debug=False):
    """
    Update the file documentation using the old docs, diffs, and additional docs.
    """
    assistant = load_assistant_agent()
    user = UserProxyAgent(name="user", code_execution_config=False)

    prompt_message = DOCUMENTATION_UPDATE_PROMPT.format(
        file_name=os.path.basename(file_path),
        old_file_docs=old_file_docs,
        old_file_content=old_file_content,
        new_file_content=new_file_content,
        diff=diff,
        changes=changes
    )
    initiate_chat(user, assistant, prompt_message)
    if save_debug:
        utils.save_prompt_debug(
            output_dir, file_path, prompt_message, utils.Mode.UPDATE)
    return assistant.last_message()['content']


@app.task(autoretry_for=(ServerError,), retry_kwargs={'max_retries': 5}, retry_backoff=True)
def get_updated_parent_documentation(file_path,
                             updated_functions,
                             additional_docs,
                             new_content,
                             functions,
                             parent_content,
                             old_parent_docs,
                             output_dir,
                             save_debug=False):
    """
    Update the parent file documentation using the filtered changes, new content, functions, and old documentation.
    """
    assistant = load_assistant_agent()
    user = UserProxyAgent(name="user", code_execution_config=False)

    prompt_message = PARENT_UPDATE.format(
        updated_function_contents=updated_functions,
        additional_docs=additional_docs,
        new_content=new_content,
        path=file_path,
        functions=functions,
        parent_content=parent_content,
        old_parent_docs = old_parent_docs
    )
    initiate_chat(user, assistant, prompt_message)
    if save_debug:
        utils.save_prompt_debug(
            output_dir, file_path, prompt_message, utils.Mode.UPDATE)
    return assistant.last_message()['content']


@app.task(autoretry_for=(ServerError,), retry_kwargs={'max_retries': 5}, retry_backoff=True)
def get_updated_commit_documentation(file_path,
                             comment,
                             file_content,
                             old_file_docs,
                             output_dir,
                             save_debug=False):
    """
    Update the file documentation based on a user comment, using the old documentation and the current file content.
    """
    assistant = load_assistant_agent()
    user = UserProxyAgent(name="user", code_execution_config=False)

    prompt_message = COMENT_UPDATE.format(
        abs_file_path=file_path,
        comment=comment,
        file_content=file_content,
        old_file_docs=old_file_docs,
    )
    initiate_chat(user, assistant, prompt_message)
    if save_debug:
        utils.save_prompt_debug(
            output_dir, file_path, prompt_message, utils.Mode.UPDATE)
    return assistant.last_message()['content']


@app.task(autoretry_for=(ServerError,), retry_kwargs={'max_retries': 5}, retry_backoff=True)
def run_multi_agent_documentation_generation(file_path, root_folder) -> str:
    os.environ["ROOT_FOLDER"] = root_folder
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
      return asyncio.run(code_context_agent.code_context_explanation(file_path))

    register_function(
      code_context_explainer,
      caller=documentation_generation_agent,
      executor=agent_manager,
      name="code_context_explainer",
      description="Generates code context description",
    )
    
    file_content = read_file_content(file_path)
    chat_result = agent_manager.initiate_chats(
        [
          {
            "recipient": documentation_generation_agent,
            "message": MULTI_AGENT_DOC_PROMPT.format(
              file_path=file_path,
              file_name=os.path.basename(file_path)
            ),
            "max_turns": 2,
            "summary_method": "last_msg",
          },
          {
            "recipient": review_agent,
            "message": REVIEWER_PROMPT,
            "max_turns": 1,
            "summary_method": "last_msg",
          },
          {
            "recipient": revise_agent,
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