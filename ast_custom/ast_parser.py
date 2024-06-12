import ast

class ASTParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = self._parse_file()

    def _parse_file(self):
        with open(self.file_path, 'r') as file:
            file_content = file.read()
        return ast.parse(file_content)

    def get_functions_and_classes(self):
        functions = []
        classes = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node)
            elif isinstance(node, ast.ClassDef):
                classes.append(node)

        return functions, classes

    def get_function_calls(self):
        calls = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                calls[func_name] = set()
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            calls[func_name].add(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            calls[func_name].add(child.func.attr)
        return {func: list(callees) for func, callees in calls.items()}


