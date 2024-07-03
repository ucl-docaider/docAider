from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex

class Retriever():
  """
  # This class offers retrieval functions in RAG architecture  
  """
  def __init__(self, ai_search_api_key, endpoint, index_name) -> None:
    """
    Initialise a new instance of the Retriever class.

    Args:
      ai_search_api_key: the api key of Azure AI Search.
      endpoint: the endpoint of Azure AI Search.
      index_name: the search index of Azure AI Search.
    """
    self.ai_search_api_key = ai_search_api_key
    self.endpoint = endpoint
    self.index_name = index_name
    # Initialize a search client using the information
    self.search_client = SearchClient(
      endpoint=endpoint, # Azure AI Search End Point
      index_name=index_name, # Azure AI Search index name
      credential=AzureKeyCredential(ai_search_api_key) # Azure AI Search API Key
    )

  def index_exist_or_not(self):
    search_index_client = SearchIndexClient(
      endpoint=self.endpoint,
      credential=AzureKeyCredential(self.ai_search_api_key)
    )
    return self.index_name in search_index_client.list_index_names()

  def create_index(self, index_name) -> None:
    """
    Creates a new search index.
    """
    index_config = {
      "client": SearchIndexClient(
        endpoint=self.endpoint,
        credential=AzureKeyCredential(self.ai_search_api_key)
      ),
      "name": index_name,
      "fields": [
        {"name": "id", "type": "Edm.String", "key": True, "filterable": False, "searchable": True},
        {"name": "filePath", "type": "Edm.String", "searchable": True},
        {"name": "content", "type": "Edm.String", "searchable": True},
        {"name": "comments", "type": "Edm.String", "searchable": True},
        {"name": "metadata", "type": "Edm.String", "searchable": False}
      ]
    }
    index = SearchIndex(name=index_config["name"], fields=index_config["fields"])
    try:
      index_config["client"].create_index(index)
      print(f"Search index {index_name} has been created successfully.")
    except:
      raise IndexAlreadyExistsError("The index already exists in the database, please try another name.")

  def upsert_documents(self, documents) -> None:
    """
    Upload new documents to the vector database.

    Args:
      documents (List[Dict]): a list of documents
    """
    try:
      self.search_client.upload_documents(documents=documents)
      print(f"New documents have been uploaded to the database successfully.")
    except:
      raise UploadDocumentFailed("The documents upload failed, please try again.")

  async def search(self, query) -> str:
    """
    Search for the query. Returns the most relevant result.
    """
    print(f"Searching...")
    results = self.search_client.search(query)
    print(f"Search completed")
    return list(results)[0]["codeSnippet"]
  
class IndexAlreadyExistsError(Exception):
  pass

class UploadDocumentFailed(Exception):
  pass