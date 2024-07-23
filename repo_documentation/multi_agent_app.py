import time, os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

from repo_agents.git_repo_agent import GitRepoAgent
from repo_documentation.merging.merger import create_documentation

def run_generate_documentation():
  """
  Invoke this function to trigger the doc gen process.
  Ensure you have all environment variables set up correctly. Check `.env_example` file to find out what they are.
  """
  start_time = time.time()
  gra = GitRepoAgent()
  gra.generate_all_documentation()
  total = round(time.time() - start_time, 3)
  if os.getenv("FORMAT") == "html":
    root_folder = os.path.abspath(os.getenv("ROOT_FOLDER"))
    output_folder = os.path.join(root_folder, "docs_output")
    create_documentation(output_folder)
  print(f"Documentation generation completed in {total}s.")

# Test it
run_generate_documentation()