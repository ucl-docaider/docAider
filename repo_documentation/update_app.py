import os, sys, time, argparse
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")
from repo_agents.documentation_update.update_agent import DocumentationUpdateAgent

class DocumentationUpdate:
  """
  This class updates documentation in two ways:
  1). Update doc based on PR comments.
  2). Update doc based on branch changes.
  Check `repo_agents/documentation_update/update_agent.py` for the update process.
  """
  def __init__(self, repo_path, branch) -> None:
    self.update_agent = DocumentationUpdateAgent(repo_path=repo_path, branch=branch)

  def run(self) -> None:
    start_time = time.time()
    self.update_agent.update_documentation()
    total = round(time.time() - start_time, 3)
    print(f"Total time taken to execute doc update: {total}s.")


if __name__ == "__main__":
  # Parse arguments
  parser = argparse.ArgumentParser(description='Update documentation based on PR comment')
  parser.add_argument('--file', type=str, help='The path of the file to update')
  parser.add_argument('--comment', type=str, help='The comment to base the update on')
  args = parser.parse_args()

  repo_path = "./../../users/"
  branch = "testing"
  file_path = args.file
  comment = args.comment

  update = DocumentationUpdate(
    repo_path=repo_path,
    branch=branch
  )
  update.run()