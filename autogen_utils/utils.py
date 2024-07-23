import os
from autogen import AssistantAgent, UserProxyAgent
from repo_documentation.prompt import DOCUMENTATION_PROMPT, \
    DOCUMENTATION_UPDATE_PROMPT, USR_PROMPT, PARENT_UPDATE, COMENT_UPDATE
from repo_documentation import utils
from . import config
from code2flow.code2flow import utils as code2flow_utils


def get_documentation(file_path,
                      file_content,
                      additional_docs,
                      user,
                      assistant,
                      output_dir,
                      root_folder,
                      save_debug=False):
    """
    Retrieves documentation for a given file.

    Args:
        file_path (str): The path of the file.
        file_content (str): The content of the file.
        additional_docs (str): Additional documentation to include.
        user (str): The user interacting with the assistant.
        assistant (Assistant): The assistant object.
        output_dir (str): The directory to save debug information.
        root_folder (str): The root folder of the project.
        save_debug (bool, optional): Whether to save debug information. Defaults to False.

    Returns:
        str: The documentation retrieved from the assistant.
    """
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


def get_updated_documentation(file_path,
                             old_file_docs,
                             old_file_content,
                             new_file_content,
                             diff,
                             additional_docs, # TODO: Add additional_docs to the prompt
                             changes,
                             user,
                             assistant,
                             output_dir,
                             save_debug=False):
    """
    Update the file documentation using the old docs, diffs, and additional docs.

    Args:
        file_path (str): The path of the file being updated.
        old_file_docs (str): The old documentation of the file.
        old_file_content (str): The old content of the file.
        new_file_content (str): The new content of the file.
        diff (str): The difference between the old and new content of the file.
        additional_docs (str): Additional documentation to be included.
        user (str): The user interacting with the assistant.
        assistant (Assistant): The assistant object used for communication.
        output_dir (str): The directory to save debug information.
        save_debug (bool, optional): Whether to save debug information. Defaults to False.

    Returns:
        str: The content of the last message from the assistant.
    """
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


def get_updated_parent_documentation(file_path,
                             updated_functions,
                             additional_docs,
                             new_content,
                             functions,
                             parent_content,
                             old_parent_docs,
                             user,
                             assistant,
                             output_dir,
                             save_debug=False):
    """
    Update the parent file documentation using the filtered changes, new content, functions, and old documentation.

    Args:
        file_path (str): The path of the parent file being updated.
        updated_functions (dict): The mapping of functions to their change contents.
        new_content (str): The new content of the parent file.
        functions (str): The functions within the parent file that are affected by the changes.
        parent_content (str): The content of the parent file.
        old_parent_docs (str): The old documentation of the parent file.
        user (UserProxyAgent): The user interacting with the assistant.
        assistant (AssistantAgent): The assistant object used for communication.
        output_dir (str): The directory to save debug information.
        save_debug (bool, optional): Whether to save debug information. Defaults to False.

    Returns:
        str: The content of the last message from the assistant.
    """
    # Convert the updated functions to a string

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

def get_updated_commit_documentation(file_path,
                             comment,
                             file_content,
                             old_file_docs,
                             user,
                             assistant,
                             output_dir,
                             save_debug=False):
    """
    Update the file documentation based on a user comment, using the old documentation and the current file content.

    Args:
        file_path (str): The path of the file being updated.
        comment (str): The user comment requesting the update.
        file_content (str): The current content of the file.
        old_file_docs (str): The old documentation of the file.
        user (UserProxyAgent): The user interacting with the assistant.
        assistant (AssistantAgent): The assistant object used for communication.
        output_dir (str): The directory to save debug information.
        save_debug (bool, optional): Whether to save debug information. Defaults to False.

    Returns:
        str: The content of the last message from the assistant.
    """
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


def get_additional_docs_path(file_path, graph, bfs_explore):
    additional_docs = ""
    file_to_calls = code2flow_utils.get_file_to_functions(graph)
    if file_path in file_to_calls:
        calls = file_to_calls[file_path]
        additional_docs += get_additional_docs_calls(calls, graph, bfs_explore)
    return additional_docs

def get_additional_docs_calls(calls, graph, bfs_explore, max_depth=5):
    additional_docs = ""
    processed_callees = set()

    for call_name in calls:
        call = graph[call_name]
        if 'EXTERNAL' in call['file_name']:
            continue
        queue = [(call_name, 0)]
        visited = set()

        while queue:
            current_call, depth = queue.pop(0)
            if depth > max_depth:
                continue
            if current_call in visited:
                continue
            visited.add(current_call)

            caller_file = graph[current_call]['file_name']

            for callee in bfs_explore.get(current_call, []):
                callee_call = graph[callee]
                callee_file = callee_call['file_name']

                if 'EXTERNAL' not in callee_file and callee not in processed_callees and caller_file != callee_file:
                    additional_docs += f"\nFunction/Class {callee_call['name']}:\n{callee_call['content']}\n"
                    processed_callees.add(callee)
                if depth < max_depth and callee not in visited:
                    queue.append((callee, depth + 1))

    return additional_docs



def load_assistant_agent():
    # Load the assistant agent for LLM-based documentation generation
    return AssistantAgent(
        name="assistant",
        system_message=USR_PROMPT,
        llm_config=config.llm_config,
        human_input_mode="NEVER"
    )


def load_user_agent():
    # Load the user agent for LLM-based documentation generation
    return UserProxyAgent(
        name="user",
        code_execution_config=False,
    )


def initiate_chat(user: UserProxyAgent, assistant, prompt):
    user.initiate_chat(
        assistant,
        message=prompt,
        max_turns=1,
        silent=True
    )


def last_message(assistant):
    return assistant.last_message()['content']
