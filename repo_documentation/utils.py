import json
import os
from enum import Enum
import sys

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from cache.docs_cache import DocsCache

class Mode(Enum):
    CREATE = 1
    UPDATE = 2


def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def get_cache(output_dir):
    cache_path = os.path.join(output_dir, 'cache.json')
    assert os.path.exists(cache_path), f"Cache file not found at {cache_path}"
    with open(cache_path, 'r', encoding='utf-8') as file:
        return DocsCache().from_dict(json.load(file))


def save_cache(output_dir, cache : DocsCache):
    cache_path = os.path.join(output_dir, 'cache.json')
    with open(cache_path, 'w', encoding='utf-8') as file:
        json.dump(cache.to_dict(), file, indent=4)


def save_prompt_debug(output_dir, file_path, prompt_message, mode):
    # Create prompt debug output directory if it doesn't exist
    debug_output_dir = os.path.join(output_dir, 'prompt_debug')
    os.makedirs(debug_output_dir, exist_ok=True)
    
    # Find path where to save the debug prompt
    project_relative_path = __get_project_relative_path(output_dir, file_path)

    # Create a dir that matches original project structure
    debug_target_dir = os.path.join(debug_output_dir, project_relative_path)
    os.makedirs(debug_target_dir, exist_ok=True)
    
    # Construct the file name (e.g. CREATE_api.py.txt)
    file_name = f'{mode.name}_{os.path.basename(file_path)}.txt'
    path = os.path.join(debug_target_dir, file_name)
    
    # path = os.path.join(debug_output_dir, file_name)
    print(f'Saving prompt debug to {path}')
    with open(path, 'w', encoding='utf-8') as file:
        file.write(prompt_message)
        
        
def save_response_debug(output_dir, file_path, prompt_response, mode):
    # Create response debug output directory if it doesn't exist
    debug_output_dir = os.path.join(output_dir, 'response_debug')
    os.makedirs(debug_output_dir, exist_ok=True)
    
    # Find path where to save the debug prompt
    project_relative_path = __get_project_relative_path(output_dir, file_path)

    # Create a dir that matches original project structure
    debug_target_dir = os.path.join(debug_output_dir, project_relative_path)
    os.makedirs(debug_target_dir, exist_ok=True)
    
    # Construct the file name (e.g. CREATE_api.py.txt)
    file_name = f'{mode.name}_{os.path.basename(file_path)}.txt'
    path = os.path.join(debug_target_dir, file_name)
    
    # path = os.path.join(debug_output_dir, file_name)
    print(f'Saving response debug to {path}')
    with open(path, 'w', encoding='utf-8') as file:
        file.write(prompt_response)
        

def write_file_docs(output_dir, root_folder, file_path, docs) -> str:
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get the path that relative from root folder
    project_relative_path = __get_project_relative_path(root_folder, file_path)
    target_dir = os.path.join(output_dir, project_relative_path)
    os.makedirs(target_dir, exist_ok=True)
    
    # Prepare the output file path
    file_name = f'{os.path.basename(file_path)}.html'
    path = os.path.join(target_dir, file_name)
    
    print(f'Saving documentation to {path}')
    with open(path, 'w', encoding='utf-8') as file:
        file.write(docs)
    return path


def __get_project_relative_path(output_dir, file_path):
    project_relative_path = os.path.relpath(file_path, output_dir)
    normalized = os.path.normpath(project_relative_path)
    split = normalized.split(os.sep)
    
    # Check if we are in the root, then return empty string
    if __is_root(split):
        return ''
   
    if split[0] == '..': # Remove the first '..'
        split = split[1:]
    if len(split) > 1: # Remove the file name
        split = split[:-1]
    return os.path.join(*split)

def __is_root(split):
    fst = split[0]
    if len(split) == 1 and (fst.endswith('.py') or fst == '..'):
        return True
    if len(split) == 2 and fst == '..' and split[1].endswith('.py'):
        return True
    return False