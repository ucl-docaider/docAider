DOCUMENTATION_PROMPT = """You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

The path of the document you need to generate in this project is {root_folder}.
Now you need to generate a document for "{file_name}".

The content of the code is as follows:
{file_content}

You must obey the structure and format that will be provided below. 

The output you produce will be placed within another HTML document, so you should not include any additional HTML tags in your response.

Please generate the documentation using the following HTML structure and CSS classes:

<h1>{file_name}</h1>
<div class="class-section">
    <h2>ClassDef NameOfClass</h2>
    <p>The function of the class is XXX. (Only code name and one sentence function description are required)</p>

    <h3>Attributes:</h3>
    <ul class="attribute-list">
        <li><code>attribute1</code> (<code>type</code>): Description of the first attribute.</li>
    </ul>

    <h3>Functions:</h3>
    <ul class="function-list">
        <li>
            <code>function_name1</code>(<code>param1</code>: <code>type</code>) -> <code>return_type</code>
            <ul>
                <li>Parameters:
                    <ul>
                        <li><code>param1</code> (<code>type</code>): Description of the first parameter.</li>
                    </ul>
                </li>
                <li>Returns:
                    <ul>
                        <li><code>return_type</code>: Description of the return value.</li>
                    </ul>
                </li>
            </ul>
        </li>
    </ul>

    <h3>Called_functions:</h3>
    <ul class="called-functions-list">
        <li><code>function1</code>(<code>param1</code>: <code>type</code>) -> <code>return_type</code>: Description of
            what function1 does and what function1 returns.</li>
    </ul>

    <h3>Code Description:</h3>
    <p>The description of this class. (Detailed and CERTAIN code analysis and description)</p>

    <h3>Note:</h3>
    <p>Points to note about the use of the code according to the returns</p>

    <h3>Input Example:</h3>
    <pre><code>
Provide an input example for a specified data type (e.g., list, double, int) and include a detailed explanation.
Remove any leading/trailing whitespaces from the output.
        </code></pre>

    <h3>Output Example:</h3>
    <pre><code>
Provide an output example for a specified data type (e.g., list, double, int) and include a detailed explanation.
Remove any leading/trailing whitespaces from the output.
         </code></pre>
</div>

<div class="function-section">
    <h2>FunctionDef NameOfFunction</h2>
    <p>The function of the function is XXX. (Only code name and one sentence function description are required)</p>

    <h3>Parameters:</h3>
    <ul class="parameter-list">
        <li><code>param1</code> (<code>type</code>): Description of the first parameter.</li>
    </ul>

    <h3>Returns:</h3>
    <ul class="return-list">
        <li><code>return_type</code>: Description of the return value.</li>
    </ul>

    <h3>Called_functions:</h3>
    <ul class="called-functions-list">
        <li><code>function1</code>(<code>param1</code>: <code>type</code>) -> <code>return_type</code>: Description of
            what function1 does and what function1 returns.</li>
    </ul>

    <h3>Code Description:</h3>
    <p>The description of this function. (Detailed and CERTAIN code analysis and description)</p>

    <h3>Note:</h3>
    <p>Points to note about the use of the code according to the returns</p>

    <h3>Input Example:</h3>
    <pre><code>
Provide an input example for a specified data type (e.g., list, double, int) and include a detailed explanation.
Remove any leading/trailing whitespaces from the output.
    </code></pre>

    <h3>Output Example:</h3>
    <pre><code>
Provide an output example for a specified data type (e.g., list, double, int) and include a detailed explanation.
Remove any leading/trailing whitespaces from the output.
    </code></pre>
</div>

Please generate a detailed explanation document for this object based on the code of the target object itself. For the section Called_functions, considering the additional documentation for the functions and classes called within the file:
{additional_docs}.

Remember to only use the HTML tags provided as shown in the template above. This structure will ensure that the documentation is properly formatted.
"""

DOCUMENTATION_UPDATE_PROMPT = """You are an AI documentation assistant. Your task is to update the existing documentation based on the provided changes in the code. 

Now you need to update the document for "{file_name}".

**Old Documentation**:
{old_file_docs}

**Old Code Content**:
{old_file_content}

**New Code Content**:
{new_file_content}

**Diff between Old and New Code**:
{diff}

**Changes in the Functions**:
{changes}

Please update the documentation accordingly, ensuring it accurately reflects the changes. Provide a comprehensive and clear description for any modified or new functions/classes.

**Note**: DO NOT CHANGE ANYTHING IN THE OLD DOCUMENTATION THAT HAS NOT BEEN AFFECTED BY THE CODE CHANGES.
"""

USR_PROMPT = """You are a documentation generation assistant for Python programs. Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way."""


PARENT_UPDATE = """

**The following functions:**
{updated_function_contents}

**In the file below:**
{new_content}

Have been updated. These changes influence the current file on the path: 
{path}

Please make sure to update the following functions in the file accordingly.
{functions}
File content:
{parent_content}
Old documentation:
{old_parent_docs}
••Note:••: DO NOT CHANGE ANYTHING IN THE OLD DOCUMENTATION THAT HAS NOT BEEN AFFECTED BY THE CODE CHANGES.

"""

COMENT_UPDATE = """The user has requested an update for the documentation in the file {abs_file_path} with the following comment:
{comment}
Please update the documentation accordingly. The current content of the file is as follows:
{file_content}
The old documentation is as follows:
{old_file_docs}

Please provide the updated documentation content. DO NOT CHANGE ANYTHING IN THE OLD DOCUMENTATION THAT HAS NOT BEEN MENTIONED IN THE COMMENT.
"""
