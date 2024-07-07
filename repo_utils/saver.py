import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from repo_utils.github_manager import GithubManager
from rag.retriever import Retriever
from exceptions import RepoLoadFailed

class RepoSaver():
  """
  This class saves all of the files in a repository into Azure AI Search index.
  """
  def __init__(self, repo_name) -> None:
    """
    Args:
      repo_name: the repository name has the form "owner/repo-name", for example, "Michael/Hello-World". 
    """
    self.repo_name = repo_name
    self.access_token = os.getenv("GITHUB_ACCESS_TOKEN")

    try:
      self.gm =  GithubManager(repo_name, self.access_token)
    except:
      raise RepoLoadFailed(f"Repo instance can not be created. Please provide valid repo name and access token.")

    self.retriever = Retriever(
      ai_search_api_key=os.getenv("AZURE_KEY_CREDENTIAL"),
      endpoint=os.getenv("SEARCH_ENDPOINT"),
      index_name="repo-index"
    )
    if not self.retriever.index_exist_or_not():
      self.retriever.create_index(self.retriever.index_name)

  def auto_save_all_files(self):
    """
    Save all of the files in the repository.
    """
    all_files = self.gm.get_all_files()
    document_count = self.retriever.search_client.get_document_count()
    print(f"Reading the repo {self.repo_name} and saving files...")
    for file in all_files:
      if self.gm.get_file_type(file) == "file":
        decoded_content = self.gm.repo.get_contents(file).decoded_content
        if self.gm.is_ascii(decoded_content):
          file_content  = decoded_content.decode("utf-8")
          document = {
            "id": str(document_count),
            "filePath": file,
            "content": file_content,
            "comments": "" # set to be empty string temporarily
          }
          self.retriever.upsert_documents([document])
          print(f"{file} saved.")
          document_count += 1
    self.gm.g.close() # Close connections

  def auto_save_python_and_md_files(self):
    """
    Save all of the Python files and markdown files in the repository.
    """
    all_files = self.gm.get_all_files()
    document_count = self.retriever.search_client.get_document_count()
    print(f"Reading the repo {self.repo_name} and saving python and markdown files...")
    for file in all_files:
      if file.endswith(".py") or file.endswith(".md"):
        file_content = self.gm.repo.get_contents(file).decoded_content.decode("utf-8")
        document = {
          "id": str(document_count),
          "filePath": file,
          "content": file_content,
          "comments": "" # set to be empty string temporarily
        }
        self.retriever.upsert_documents([document])
        print(f"{file} saved.")
        document_count += 1
    self.gm.g.close() # Close connections