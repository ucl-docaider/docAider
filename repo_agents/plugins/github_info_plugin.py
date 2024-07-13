import os
from github import Github
from github import Auth
from semantic_kernel.functions import kernel_function
from typing import Annotated

class GithubInfoPlugin:
  def __init__(self) -> None:
    """
    Initialise a new instance of the GithubManager class.

    Args:
      repo_name: the repository name has the form "owner/repo-name", for example, "Michael/Hello-World".
      access_token: your Github access token. Ensure this token includes the `repo` scope so that repo information can be accessed. To learn how to manage your access tokens, see https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
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