import os
import datetime
import time
from autogen import AssistantAgent, UserProxyAgent
from utils import build_tree_and_relationships, save_to_json

# Documentation Generation Code
print("Starting the documentation generation process...")

llm_config = {
  "model": "llama3",
  "base_url": "http://localhost:11434/v1",
  "api_key": "ollama",
}

assistant = AssistantAgent(
  name="assistant",
  system_message="You are a documentation generation assistant for Python programs",
  llm_config=llm_config,
  human_input_mode="NEVER"
)

user = UserProxyAgent(
  name="user",
  code_execution_config=False,
)

# Profile (start)
start_time = time.time()

# Prompt template
prompt_template = """
Please provide a short and code level documentation for the following file content:

File: {file_name}
Content:
{file_content}

Consider the additional documentation for the functions and classes called within the file:
{additional_docs}

Below is a prompt template that you need to use for the GitHub documentation:
Project Name
1. Description
A brief overview of what the project does, its purpose, and key features.

2. Classes and Functions
    - Class 1
        -- Attributes
            --- attribute1 (type): Description of the first attribute.
            --- attribute2 (type): Description of the second attribute.
        -- Functions
            --- function_name(param1: type, param2: type) -> return_type
                ---- Parameters:
                    ----- param1 (type): Description of the first parameter.
                    ----- param2 (type): Description of the second parameter.
                ---- Returns:
                    ----- return_type: Description of the return value.
            --- Called_functions: List of functions called within this function and short description of what they do.
                ---- function1: Description of what function1 does.
                ---- function2: Description of what function2 does.   
    - Function 1 (functions that do not belong to a class but are still present in the file)
        -- Parameters:
            --- param1 (type): Description of the first parameter.
            --- param2 (type): Description of the second parameter.
        -- Returns:
            --- return_type: Description of the return value.
        -- Called_functions: List of functions called within this function and a short description of what they do.
            --- function1: Description of what function1 does.
            --- function2: Description of what function2 does.
"""

# Generate documentation for each file in the project
root_folder = './test'
output_file = 'output.json'

tree, relationships, file_contents = build_tree_and_relationships(root_folder)

save_to_json(tree, relationships, output_file)

def get_code_snippet(file_path, function_name):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    code_snippet = ""
    inside_function = False
    for line in lines:
        if line.strip().startswith(f"def {function_name}(") or line.strip().startswith(f"class {function_name}("):
            inside_function = True
        if inside_function:
            code_snippet += line
            if line.strip() == "":
                break
    return code_snippet

def generate_function_doc(assistant, user, file_name, file_content, called_functions):
    additional_docs = ""
    for func in called_functions:
        for path, content in file_contents.items():
            if f"def {func}(" in content or f"class {func}(" in content:
                additional_docs += f"\nFunction/Class {func}:\n{get_code_snippet(os.path.join(root_folder, path), func)}\n"
                break

    prompt_message = prompt_template.format(
        file_name=file_name,
        file_content=file_content,
        additional_docs=additional_docs
    )

    user.initiate_chat(
        assistant,
        message=prompt_message,
        max_turns=1,
        silent=True
    )

    return assistant.last_message()['content']

for file_path in tree:
    file_name = os.path.basename(file_path)
    file_content = file_contents[file_path]

    called_functions = []
    for func, calls in relationships[file_path].items():
        called_functions.extend(calls['internal'])

    documentation = generate_function_doc(assistant, user, file_name, file_content, called_functions)

    # Write the documentation to a file at /docs_output/docs.md (add timestamp to the filename)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_file = os.path.join("docs_output", f"docs_{file_name}_{timestamp}.md")
    with open(output_file, "w") as f:
        f.write(documentation)
    print(f"Documentation written to {output_file}")

# Profile (end)
total = round(time.time() - start_time, 3)
print(f"Total time taken to execute from initiate_chat: {total}s.")
