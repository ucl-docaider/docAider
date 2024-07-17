CODE_CONTEXT_PROMPT = """
First you need to get the content of this file (source code): {file_path}.

Then you need to get the information of the callee function in the same file path:
`callee function information`

The information of the callee function can help you understand the context of the APIs. Your task is to generate a brief explanation for the Python file.

Please use the following output template:

The content of the file (source code) is as follows:
`Put the file content here.`

Explanation of code context:
`Put the description of the code context here.`

Callee functions:
`Put a list of callee functions here. Ignore this section if there is no callee function.`
"""

DOCUMENTATION_PROMPT = """
You can first use the code context explainer to get the code context, then based on the contextual information, generate a documentation for the source code. 
The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Please note any part of the content you generate SHOULD NOT CONTAIN Markdown hierarchical heading and divider syntax.

The standard format is as follows (If a section does not have any information, you can skip it and move to the next one):

# {file_path}

## ClassDef NameOfClass

The function of the class is XXX. (Only code name and one sentence function description are required)

**Attributes**:

- `attribute1` (`type`): Description of the first attribute.

**Functions**:

- `function_name1`(`param1`: `type`) -> `return_type`
    - Parameters:
        - `param1` (`type`): Description of the first parameter.
    - Returns:
        - `return_type`: Description of the return value.

**Called_functions**:

- `function1`(`param1`: `type`) -> `return_type`: Description of what function1 does and what function1 returns.

**Code Description**: The description of this class. (Detailed and CERTAIN code analysis and description)

**Note**: Points to note about the use of the code according to the returns

**Input Example**: 

```
Provide an input example for a specified data type (e.g., list, double, int) and include a detailed explanation.
```

**Output Example**:

```
Provide an output example for a specified data type (e.g., list, double, int) and include a detailed explanation.
```


## FunctionDef NameOfFunction (functions that do not belong to a class but are still present in the file)

The function of the function is XXX. (Only code name and one sentence function description are required)

**Parameters**:

- `param1` (`type`): Description of the first parameter.

**Returns**:

- `return_type`: Description of the return value.

**Called_functions**:

- `function1`(`param1`: `type`) -> `return_type`: Description of what function1 does and what function1 returns.

**Code Description**: The description of this function. (Detailed and CERTAIN code analysis and description)

**Note**: Points to note about the use of the code according to the returns

**Input Example**: 

```
Provide an input example for a specified data type (e.g., list, double, int) and include a detailed explanation.
```

**Output Example**: 

```
Provide an output example for a specified data type (e.g., list, double, int) and include a detailed explanation.
```
"""