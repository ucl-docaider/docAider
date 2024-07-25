import time, os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

from repo_agents.single_agent_generation.documentation_agent import DocumentationAgent
from repo_documentation.merging.merger import create_documentation_index

def run_generate_documentation():
  """
  Invoke this function to trigger the doc gen process (single-agent pattern).
  Tradeoff: Cheap (use fewer tokens), less accurate (lightweight generation process)
  Ensure you have all environment variables set up correctly. Check `.env_example` file to find out what they are.
  """
  start_time = time.time()
  da = DocumentationAgent()
  da.generate_all_documentation()
  total = round(time.time() - start_time, 3)
  create_documentation_index() # Create index page of documentation files
  print(f"Documentation generation completed in {total}s.")

# Test it
run_generate_documentation()