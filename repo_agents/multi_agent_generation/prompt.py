CODE_CONTEXT_PROMPT = """
First you need to get the content of this file (source code): {file_path}.
Next, gather information on all callee functions within the same file path. 
Understanding these callee functions will help you comprehend the context of the WHOLE file content.
Your task is to generate a concise yet thorough explanation for the Python file.

Please use the following output template:

The content of the file (source code) is as follows:
`Put the file content here.`

Explanation of Every Class and Function:
`Provide a detailed and thorough description of EVERY class AND function, including their purpose, functionality, and any important implementation details.`

Input/Ouput Examples:
PROVIDE INPUT AND OUTPUT EXAMPLES for EACH class AND function in the file, with detailed explanations.

Called functions information:
`Provide detailed information about called functions, including how each function interacts with other parts of the code, any relationships or dependencies, and the context in which these functions are used.`

"""

DOCUMENTATION_PROMPT = """
First you can use the code context explainer to get the code context.
Then based on the code contextual explanation, generate a documentation for the source code based on the STANDARD FORMAT. DO NOT SKIP ANY SECTION OR SUBSECTION of the STANDARD FORMAT.
The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code. INCLUDE DETAILED description for every CLASS and FUNCTION in the file.
Please ADD NOTES for any part that you are confused aboutt or if you have any suggestions to the code.

The file path is: {file_path}

The STANDARD FORMAT is as follows:

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

This is the generated documentation for the source code. Please review it and improve the documentation quality, ONLY IF NEEDED. You SHOULD NOT ADD ANY comments or notes ABOUT QUALITY to the documentation.
DO NOT DELETE/REMOVE ANY PART OF THE Context that is passed to you.
INSERT "INPUT AND OUTPUT" EXAMPLES, if it is MISSING for a specific function, in the same format as the existing examples;
RETURN THE IMPROVED DOCUMENTATION IN THE SAME FORMAT AS THE GENERATED DOCUMENTATION.
"""


USR_PROMPT = """You are a documentation generation assistant for Python programs. Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way."""
