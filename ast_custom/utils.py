from .ast_parser import ASTParser
import re, os, json, ast

def build_tree_and_relationships(root_folder, exclude_dirs_regex=r'env'):
    """
    Build the tree representation of the project's directory structure and the relationships between functions.

    Args:
        root_folder (str): The root folder of the project.
        exclude_dirs_regex (str): Regular expression pattern to exclude specific directories from the tree and relationships.

    Returns:
        tuple: A tuple containing the tree representation, the relationships between functions, and a dictionary of file contents.
    """
    tree, function_set, file_contents = __build_tree(root_folder, exclude_dirs_regex)
    relationships = __build_function_relationships(root_folder, function_set, exclude_dirs_regex)
    return tree, relationships, file_contents

# Save the tree and relationships to a JSON file
def save_to_json(tree, relationships, output_file):
    """
    Save the tree and relationships to a JSON file.
    """
    data = {
        "tree": tree,
        "relationships": relationships
    }
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def __build_tree(root_folder, exclude_dirs_regex):
    """
    Build a tree representation of the project's directory structure and extract functions and classes from Python files.

    Args:
        root_folder (str): The root folder of the project.
        exclude_dirs_regex (str): Regular expression pattern to exclude specific directories from the tree.

    Returns:
        tuple: A tuple containing the tree representation, a set of project functions, and a dictionary of file contents.
        
    The tree contains the following keys:
        'tree' (dict): A dictionary representing the project's directory structure with functions and classes. (File name -> classes/functions)
        'classes' (dict): A dictionary of classes and their methods in the given file (class name -> list of method names)
        'function_set' (set): A set of all function names in the given file
    (file_name -> {'classes': {class_name -> [method_names]}, 'functions': [function_names]})
    
    The function_set contains all the function names in the project, including those within classes.
    The file_contents dictionary contains the contents of each file in the project.    
    """
    tree = {}
    function_set = set()
    file_contents = {}

    for dirpath, dirnames, filenames in os.walk(root_folder):
        dirnames[:] = [d for d in dirnames if not re.search(exclude_dirs_regex, d)]
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(dirpath, filename)
                print(f"Parsing file: {file_path}")
                parser = ASTParser(file_path)
                functions, classes = parser.get_functions_and_classes()
                relative_path = os.path.relpath(file_path, root_folder).replace(os.sep, '/')
                tree[relative_path] = {'classes': {}, 'functions': [func.name for func in functions]}
                
                # Store file content
                with open(file_path, 'r') as file:
                    file_contents[relative_path] = file.read()

                for cls in classes:
                    class_name = cls.name
                    class_functions = [func.name for func in cls.body if isinstance(func, ast.FunctionDef)]
                    tree[relative_path]['classes'][class_name] = class_functions
                    function_set.update(class_functions)

                function_set.update(func.name for func in functions)

    return tree, function_set, file_contents


def __build_function_relationships(root_folder, function_set, exclude_dirs_regex):
    """
    Build relationships between functions in the project.

    Args:
        root_folder (str): The root folder of the project.
        function_set (set): A set of all project function names.
        exclude_dirs_regex (str): Regular expression pattern to exclude specific directories from the relationships.

    Returns:
        dict: A dictionary representing the relationships between functions in the project.
        
    The dictionary is of the following structure:
        file_name (dict): A dictionary containing function names as keys and their internal and external function calls as values.
    (file_name -> {function_name -> {"internal": [internal_function_calls], "external": [external_function_calls]}})
        
    The internal function calls are the calls to other functions within the project, while the external function calls are the calls to functions outside the project.
    """
    relationships = {}

    for dirpath, dirnames, filenames in os.walk(root_folder):
        dirnames[:] = [d for d in dirnames if not re.search(exclude_dirs_regex, d)]
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(dirpath, filename)
                parser = ASTParser(file_path)
                calls = parser.get_function_calls()
                relative_path = os.path.relpath(file_path, root_folder).replace(os.sep, '/')

                for func, callees in calls.items():
                    internal_calls = []
                    external_calls = []
                    for callee in callees:
                        if callee in function_set:
                            internal_calls.append(callee)
                        else:
                            external_calls.append(callee)
                    calls[func] = {
                        "internal": internal_calls,
                        "external": external_calls
                    }

                relationships[relative_path] = calls

    return relationships
