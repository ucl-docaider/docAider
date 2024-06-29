import asyncio, os
from generator import DocumentationGenerator

dg = DocumentationGenerator()
"""
Test creating search index
"""
#dg.retriever.create_index("code-index")

"""
Test upserting documents
"""
"""full_path = os.path.dirname(__file__) + "/../code2flow/projects/users/main.py"
with open(full_path, "r") as file:
  source_code = file.read()
documents = [
  {"id": "1", "codeSnippet": source_code, "comments": ""}
]
dg.retriever.upsert_documents(documents)"""

"""
Test Searching (Retrieval)
"""
source_code = asyncio.run(dg.retriever.search("I need code of id 1"))
print(source_code)

response = asyncio.run(dg.generate_documentation(
  file_name="main.py",
  file_content=source_code,
  root_folder="/../code2flow/projects/users",
  additional_docs="",
))
with open("rag_output.md", "w") as file:
  file.write(response)