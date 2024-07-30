CODE_CONTEXT_PROMPT = """
First you need to get the content of this file (source code): {file_path}.
Then you need to get the information of the callee function in the same file path.
The information of the callee function can help you understand the context of the APIs.
Your task is to generate a brief explanation for the code.

Please use the following output template:

The content of the file (source code) is as follows:
`Put the file content here.`

Explanation of code context:
`Put the description of the code context here.`

Callee function information:
`Put callee function information here.` (Ignore this section if there is no callee function.)
"""

DOCUMENTATION_PROMPT = """
First you can use the code context explainer to get the code context.
Then based on the code contextual explanation, generate a documentation for the source code. 
The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code. Include detailed description for every class and function in the file.
Please add notes for any part that you are confused about or if you have any suggestions to the code.
The file path is: {file_path}

# {file_name}

## Overview:
PROVIDE DETAILED OVERVIEW of the entire file, explaining its purpose, key components, and any important relationships or interactions between classes and functions.

## ClassDef NameOfClass

PROVIDE DETAILED DESCRIPTION of the Class, including a detailed analysis in plain text (including all details).
(Detailed and CERTAIN code analysis)

**Attributes (for classes)**:

- `attribute` (`type`): Description of the attribute.

## FunctionDef NameOfFunction 

PROVIDE A DETAILED DESCRIPTION of the function, including its functionality, key components and key details.
(Detailed and CERTAIN code analysis)

**Parameters**:

- `param1` (`type`): Description of the parameter.

**Returns**:

- `return_type`: Description of the return value.

## Called_functions:
PROVIDE DETAILED DESCRIPTION of what this called function does, including explanation of the interaction and the context in which it is used.

**Note**: INCLUDE any important considerations, usage notes, or potential pitfalls relevant to this class or function.

## Examples:
Provide OUTPUT/INPUT EXAMPLES FOR EACH FUNCTION/CLASS.
**Input Examples**: 

```
Provide an input examples for a specified data type (e.g., list, double, int) and include a detailed explanation.
```

**Output Example**:

```
Provide an output example for a specified data type (e.g., list, double, int) and include a detailed explanation.
```
"""

REVIEWER_PROMPT = """
The file content (source code):
{file_content}
(-Source code ends-)

This is the generated documentation for the source code. Please check its quality and accuracy, and provide suggestions for improvement.
Note: Do not change the documentation, your task is to review and comment it.
Please use the following output template:
`Generated documentation`
(-Documentation ends-)

Reviewer agent comments:
`Put your comments and suggestions for improvement here`
"""

REVISOR_PROMPT = """
This is the code-level documentation and review agent's comments. Please improve the documentation according to the comments.
Your output should be a formal markdown documentation. 
"""