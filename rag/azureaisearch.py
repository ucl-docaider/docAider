import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex

# Create a search client using environment variables
search_client = SearchClient(
  endpoint=os.environ["SEARCH_ENDPOINT"],
  index_name="code-index",
  credential=AzureKeyCredential(os.environ["AZURE_KEY_CREDENTIAL"])
)

# This part contructed a new search index and inject documents to the index
"""
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

# Ask the search client to return response for a search query
results = search_client.search("I need a code snippet that adds three numbers")
print(f"Searching...")
print(f"-------------------------------------")
for result in list(results):
  print(f"Relevancy score: {result['@search.score']}")
  print(f"The search result: {result['codeSnippet']}")
  print(f"Document ID: {result['id']}")
  print(f"Code comments: {result['comments']}")
  print(f"-------------------------------------")