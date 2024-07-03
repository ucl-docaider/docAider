import asyncio, os
from retriever import Retriever
from generator import DocumentationGenerator

dg = DocumentationGenerator("mistral")
"""
Test searching (Retrieval) and generation
"""
source_code = asyncio.run(dg.context_retriever.search("../code2flow/projects/users/main.py"))
print(source_code)

response = asyncio.run(dg.generate_documentation(
  file_path="../code2flow/projects/users/main.py",
  file_content=source_code,
  root_folder="/../code2flow/projects/users",
  additional_docs="",
))
with open("rag_output.md", "w") as file:
  file.write(response)