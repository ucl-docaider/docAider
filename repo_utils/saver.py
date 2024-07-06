import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from github_manager import GithubManager
from rag.retriever import Retriever
from exceptions import RepoLoadFailed

"""
This script saves all of the files in a repository into Azure AI Search index.
Prepare 
"""
# Ask users for the repo information
repo_name = input(f"Please provide the repository name: ")
access_token = input(f"Please provide your Github access token: ")

try:
  gm =  GithubManager(repo_name, access_token)
except:
  raise RepoLoadFailed(f"Repo instance can not be created. Please provide valid repo name and access token.")

retriever = Retriever(
  ai_search_api_key=os.getenv("AZURE_KEY_CREDENTIAL"),
  endpoint=os.getenv("SEARCH_ENDPOINT"),
  index_name="repo-index"
)
if not retriever.index_exist_or_not():
  retriever.create_index(retriever.index_name)

def auto_save_all_files():
  """
  Save all of the files in the repository.
  """
  all_files = gm.get_all_files()
  document_count = retriever.search_client.get_document_count()
  print(f"Reading the repo {repo_name} and saving files...")
  for file in all_files:
    if gm.get_file_type(file) == "file":
      decoded_content = gm.repo.get_contents(file).decoded_content
      if gm.is_ascii(decoded_content):
        file_content  = decoded_content.decode("utf-8")
        document = {
          "id": str(document_count),
          "filePath": file,
          "content": file_content,
          "comments": "" # set to be empty string temporarily
        }
        retriever.upsert_documents([document])
        print(f"{file} saved.")
        document_count += 1
  gm.g.close() # Close connections

def auto_save_python_and_md_files():
  """
  Save all of the Python files and markdown files in the repository.
  """
  all_files = gm.get_all_files()
  document_count = retriever.search_client.get_document_count()
  print(f"Reading the repo {repo_name} and saving python and markdown files...")
  for file in all_files:
    if file.endswith(".py") or file.endswith(".md"):
      file_content = gm.repo.get_contents(file).decoded_content.decode("utf-8")
      document = {
        "id": str(document_count),
        "filePath": file,
        "content": file_content,
        "comments": "" # set to be empty string temporarily
      }
      retriever.upsert_documents([document])
      print(f"{file} saved.")
      document_count += 1
  gm.g.close() # Close connections

auto_save_python_and_md_files()