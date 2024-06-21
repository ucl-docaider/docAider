import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex

# This module manages Azure AI Search functions

# Create a search client using environment variables
search_client = SearchClient(
  endpoint=os.environ["SEARCH_ENDPOINT"], # Azure AI Search End Point
  index_name="code-index", # Azure AI Search index name
  credential=AzureKeyCredential(os.environ["AZURE_KEY_CREDENTIAL"]) # Azure AI Search API Key
)
"""
# This part contructed a new search index and inject documents to the index
# Create an index
index_config = {
  "client": SearchIndexClient(
    endpoint=os.environ["SEARCH_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_KEY_CREDENTIAL"])
  ),
  "name": "code-index",
  "fields": [
    {"name": "id", "type": "Edm.String", "key": True, "filterable": False, "searchable": False},
    {"name": "codeSnippet", "type": "Edm.String", "searchable": True},
    {"name": "comments", "type": "Edm.String", "searchable": True},
    {"name": "metadata", "type": "Edm.String", "searchable": False}
  ]
}
index = SearchIndex(name=index_config["name"], fields=index_config["fields"])
result = index_config["client"].create_index(index)

# Example data to index
documents = [
  {"id": "1", "codeSnippet": "def add(a, b): return a + b", "comments": "Adds two numbers"},
  {"id": "2", "codeSnippet": "def subtract(a, b): return a - b", "comments": "Subtracts two numbers"},
  {"id": "3", "codeSnippet": "def multiply(a, b): return a * b", "comments": "Multiplies two numbers"},
  {"id": "4", "codeSnippet": "def add(a, b, c): return a + b + c", "comments": "Adds three numbers"}
]

result = search_client.upload_documents(documents=documents)
print("Upload of new document succeeded: {}".format(result[0].succeeded))
"""

# Test the search function
# Ask the search client to return response based on a search query
results = search_client.search("I need a code snippet from id 2")
print(f"Searching...")
print(f"-------------------------------------")
for result in list(results):
  print(f"Relevancy score: {result['@search.score']}")
  print(f"The search result: {result['codeSnippet']}")
  print(f"Document ID: {result['id']}")
  print(f"Code comments: {result['comments']}")
  print(f"-------------------------------------")