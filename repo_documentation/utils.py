from ast_parser import ASTParser
import re, os, json, ast

def build_tree(root_folder, exclude_dirs_regex):
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

def build_function_relationships(root_folder, project_functions, exclude_dirs_regex):
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
                        if callee in project_functions:
                            internal_calls.append(callee)
                        else:
                            external_calls.append(callee)
                    calls[func] = {
                        "internal": internal_calls,
                        "external": external_calls
                    }

                relationships[relative_path] = calls

    return relationships

def save_to_json(tree, relationships, output_file):
    data = {
        "tree": tree,
        "relationships": relationships
    }
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def build_tree_and_relationships(root_folder):
    exclude_dirs_regex = r'env'
    tree, project_functions, file_contents = build_tree(root_folder, exclude_dirs_regex)
    relationships = build_function_relationships(root_folder, project_functions, exclude_dirs_regex)
    return tree, relationships, file_contents