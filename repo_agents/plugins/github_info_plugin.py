import os
import chardet
from github import Github
from github import Auth
from semantic_kernel.functions import kernel_function
from typing import Annotated

class GithubInfoPlugin:
  def __init__(self) -> None:
    """
    This is a plugin for providing github related information.
    You need to store Github access token in your .env file. Ensure this token includes the `repo` scope so that repo information can be accessed. To learn how to manage your access tokens, see https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
    """
    self.g = Github(auth=Auth.Token(os.getenv("GITHUB_ACCESS_TOKEN")))

  @kernel_function(
    name="get_all_repos",
    description="Gets all of my repositories"
  )
  def get_all_repos(self) -> Annotated[list, "A list of repository names"]:
    repos = []
    for repo in self.g.get_user().get_repos():
      repos.append(repo.name)
    self.g.close()
    return repos
  
  @kernel_function(
    name="get_repo_owner",
    description="Gets the owner of the repository"
  )
  def get_repo_owner(self, repo_name: Annotated[str, "Repository name"]) -> Annotated[str, "The owner name of the repository"]:
    for repo in self.g.get_user().get_repos():
      if repo.name == repo_name:
        return repo.owner.login
  
  @kernel_function(
    name="get_branches",
    description="Gets all branches of the repository"
  )
  def get_branches(self, repo_name: Annotated[str, "Repository name"]) -> Annotated[list, "A list of branches of the repository"]:
    repo_owner = self.get_repo_owner(repo_name)
    branches = []
    for b in self.g.get_repo(repo_owner + "/" + repo_name).get_branches():
      branches.append(b.name)
    self.g.close()
    return branches
  
  @kernel_function(
    name="get_all_files_in_repo",
    description="Gets all of the files in a repository."
  )
  def get_all_files_in_repo(
    self,
    repo_name: Annotated[str, "The repository name"]
  ) -> Annotated[list, "A list of files in a repository"]:
    """
    Returns all of the files in a repository (Including submodules).
    """
    repo_owner = self.get_repo_owner(repo_name)
    repo = self.g.get_repo(repo_owner + "/" + repo_name)
    contents = repo.get_contents("")
    files = []
    while contents:
      file_content = contents.pop(0)
      if file_content.type == "dir":
        contents.extend(repo.get_contents(file_content.path))
      else:
        files.append(file_content.path)
    return files
  
  @kernel_function(
    name="get_file_content",
    description="Returns the file content"
  )
  def get_file_content(
    self,
    file_name: Annotated[str, "The file name"],
    repo_name: Annotated[str, "The repository name"]
  ) -> Annotated[str, "The content of the file"]:
    """
    Returns the content of a file in the repo.
    """
    repo_owner = self.get_repo_owner(repo_name)
    repo = self.g.get_repo(repo_owner + "/" + repo_name)
    decoded_content = repo.get_contents(file_name).decoded_content
    if self._is_ascii(decoded_content):
      return decoded_content.decode("utf-8")
    else:
      return ""
    
  def _is_ascii(self, decoded_content):
    """
    Returns True if the decoded_content is ASCII, False otherwise.
    """
    result = chardet.detect(decoded_content)
    encoding = result["encoding"]
    return encoding == "ascii"