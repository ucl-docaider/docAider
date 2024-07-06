from github import Github
from github import Auth
import chardet

class GithubManager():
  """
  This class provides functions of managing Github repositories.
  See https://pygithub.readthedocs.io/en/latest/examples/Repository.html for Github API documentation.
  """

  def __init__(self, repo_name, access_token) -> None:
    """
    Initialise a new instance of the GithubManager class.

    Args:
      repo_name: the repository name has the form "owner/repo-name", for example, "Michael/Hello-World".
      access_token: your Github access token. Ensure this token includes the `repo` scope so that repo information can be accessed. To learn how to manage your access tokens, see https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
    """
    self.g = Github(auth=Auth.Token(access_token))
    self.repo = self.g.get_repo(repo_name)

  def get_all_files(self) -> list:
    """
    Returns all of the files in a repository (Including submodules).
    """
    contents = self.repo.get_contents("")
    files = []
    while contents:
      file_content = contents.pop(0)
      if file_content.type == "dir":
        contents.extend(self.repo.get_contents(file_content.path))
      else:
        files.append(file_content.path)
    return files

  def get_file_content(self, file) -> str:
    """
    Returns the content of a file in the repo.
    """
    decoded_content = self.repo.get_contents(file).decoded_content
    if self._is_ascii(decoded_content):
      return decoded_content.decode("utf-8")
  
  def get_file_type(self, file) -> str:
    """
    Returns the type of a file, e.g., file, dir, submodule, etc.
    """
    return self.repo.get_contents(file).type

  def is_ascii(self, decoded_content):
    """
    Returns True if the decoded_content is ASCII, False otherwise.
    """
    result = chardet.detect(decoded_content)
    encoding = result["encoding"]
    return encoding == "ascii"