CODE_CONTEXT_PROMPT = """
First you need to find the content of the file (source code): {file_name}.

Then you need to find the information of the callee function in the source code for this file path: {file_path}
`callee function information`

The information of the called function can help you understand the context of the APIs. Your task is to generate a brief explanation for the Python file.

Please use the following output template:

The content of the file (source code) is as follows:
`Put the file content here.`

Explanation of code context:
`Put the description of the code context here.`

Called functions:
`Put a list of called functions here. Ignore this section if there is no called function.`
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