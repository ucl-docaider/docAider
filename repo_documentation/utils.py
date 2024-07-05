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
    with open(file_path, 'r') as file:
        return file.read()


def get_cache(output_dir):
    cache_path = os.path.join(output_dir, 'cache.json')
    assert os.path.exists(cache_path), f"Cache file not found at {cache_path}"
    with open(cache_path, 'r') as file:
        return DocsCache().from_dict(json.load(file))


def save_cache(output_dir, cache : DocsCache):
    cache_path = os.path.join(output_dir, 'cache.json')
    with open(cache_path, 'w') as file:
        json.dump(cache.to_dict(), file, indent=4)


def save_prompt_debug(output_dir, file_name, prompt_message, mode):
    base_name = os.path.basename(file_name)
    file_name = f'{mode.name}_{base_name}.txt'
    debug_output_dir = os.path.join(output_dir, 'prompt_debug')
    os.makedirs(debug_output_dir, exist_ok=True)
    path = os.path.join(debug_output_dir, file_name)
    with open(path, 'w') as file:
        file.write(prompt_message)


def write_file_docs(output_dir, root_folder, file_path, docs) -> str:
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get the path that relative from root folder
    rel_path = os.path.relpath(file_path, root_folder)

    # Write the docs to a markdown file
    rel_path += '.md'
    output_file_path = os.path.join(output_dir, rel_path)
    with open(output_file_path, 'w') as file:
        file.write(docs)
    return output_file_path