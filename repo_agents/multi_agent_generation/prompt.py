CODE_CONTEXT_PROMPT = """
First you need to get the content of this file (source code): {file_path}.
Next, gather information on all callee functions within the same file path. 
Understanding these callee functions will help you comprehend the context of the WHOLE file content.
Your task is to generate a concise yet thorough explanation for the Python file.

Please use the following output template:

The content of the file (source code) is as follows:
`Put the file content here.`

Explanation of Every Class and Function:
`Provide a detailed and thorough description of every class and function, including their purpose, functionality, and any important implementation details.`

Input/Ouput Examples:
Provide input and output examples for each class and function in the file, with detailed explanations.

Called functions information:
`Provide detailed information about called functions, including how each function interacts with other parts of the code, any relationships or dependencies, and the context in which these functions are used.`

"""

DOCUMENTATION_PROMPT = """
First you can use the code context explainer to get the code context.
Then based on the code contextual explanation, generate a documentation for the source code based on the Standard Markdown Format. DO NOT SKIP any section or subsection of the Standard Format.
The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code. INCLUDE DETAILED description for EVERY CLASS and FUNCTION in the file.
Please add notes for any part that you are confused aboutt or if you have any suggestions to the code.

The file path is: {file_path}

The Standard Markdown Format is as follows:

# {file_name}

## Overview:
PROVIDE DETAILED OVERVIEW of the entire file, explaining its purpose, key components, and any important relationships or interactions between classes and functions.

## ClassDef NameOfClass or FunctionDef NameOfFunction 

PROVIDE DETAILED DESCRIPTION of the Class or Function, including a detailed analysis in plain text (including all details).
(Detailed and CERTAIN code analysis)

### Method NameOfMethod (method BELONGING to a class)
PROVIDE A DETAILED DESCRIPTION of the Method, including its functionality, key components and key details.
(Detailed and CERTAIN code analysis)

**Parameters**:

**Returns**:

**Note**: INCLUDE any important considerations, usage notes, or potential pitfalls relevant to this class or Method.

#### Examples:
Provide output/input examples for EACH METHOD.
**Input Examples**: 

```
Provide an input examples for a specified data type (e.g., list, double, int) and include a detailed explanation.
```

**Output Example**:

```
Provide an output example for a specified data type (e.g., list, double, int) and include a detailed explanation.
```

## FunctionDef NameOfFunction (functions that DOES NOT BELONG to a class but are still present in the file)

PROVIDE A DETAILED DESCRIPTION of the function, including its functionality, key components and key details.
(Detailed and CERTAIN code analysis)

**Parameters**:

**Returns**:

**Note**: INCLUDE any important considerations, usage notes, or potential pitfalls relevant to this class or function.

### Examples:
Provide output/input examples for each FUNCTION.
**Input Examples**: 

```
Provide an input examples for a specified data type (e.g., list, double, int) and include a detailed explanation.
```

**Output Example**:

```
Provide an output example for a specified data type (e.g., list, double, int) and include a detailed explanation.
```

## Called_functions:
PROVIDE DETAILED DESCRIPTION of what every called functions does, including explanation of the interaction and the context in which it is used.
"""

REVIEWER_PROMPT = """

This is the generated documentation for the source code. Please check its quality and accuracy, and provide suggestions for improvement. Your Suggestions HAVE TO BE specific and clear, so that the revisor can EASILY understand and implement them WITHOUT the knowledge of codebase.
Note: 
1. DO NOT change the documentation, your task is to review and provide suggestions for it.
2. Your suggestions should not contain REMOVE/DELETE instructions.
3. Your suggestions may involve ADDING Function Description for missing functions, Input/Output examples for missing functions to the ##Examples section, or improving the clarity of the documentation.
Please use the following output template:
`Generated documentation`
(-Documentation ends-)

Reviewer agent sugesstions:
`Put your comments and suggestions for improvement here`


"""


REVISOR_PROMPT = """
The file content (source code):
{file_content}
(-Source code ends-)

This is the code-level documentation for the source code and Reviewer agent's comments. Please IMPROVE the documentation according to the SUGGESTIONS, which involves adding missing function descriptions, input/output examples, or improving the clarity of the documentation. 
DO NOT DELETE/REMOVE any part of the existing documentation.
Your output should be the SAME FORMAT as the existing documentation, with the necessary improvements. 
"""