import time, os, sys
import markdown
from weasyprint import HTML
from google.genai.errors import ClientError

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from dotenv import load_dotenv
load_dotenv(dotenv_path="./.env")

_root_folder = os.getenv("ROOT_FOLDER")
if not _root_folder or _root_folder == "/":
    os.environ["ROOT_FOLDER"] = parent_dir
_root_folder = os.environ["ROOT_FOLDER"] # get updated value

from repo_agents.ast_agent import ASTAgent
import repo_agents.multi_agent_generation.multi_agent_conversation as mac

def run_generate_documentation_for_file(file_path: str):
  """
  Generates documentation for a single file using the multi-agent system and saves it as a PDF.
  """
  start_time = time.time()

  # Ensure call graph exists for context analysis. The ASTAgent constructor does this.
  print("Generating call graph for context analysis...")
  ASTAgent()
  print("Call graph generated.")
  
  print(f"Generating documentation for {file_path} using multi-agent system...")
  # This function orchestrates the multi-agent conversation and returns the final markdown.
  
  wait_times = [1, 2, 4, 8, 16, 32]
  markdown_content = None
  for i, wait_time in enumerate(wait_times):
      try:
          markdown_content = mac.multi_agent_documentation_generation(file_path)
          break  # Success
      except ClientError as e:
          if "429" in str(e) and i < len(wait_times) - 1:
              print(f"Rate limit exceeded. Retrying in {wait_time}s...")
              time.sleep(wait_time)
          else:
              raise e
  
  if not markdown_content or "failed to run" in markdown_content:
      print(f"Error: Multi-agent documentation generation failed for {file_path}")
      print("Agent returned:", markdown_content)
      return

  print("Documentation generation complete. Converting to PDF...")
      
  # Convert markdown to HTML
  html_content = markdown.markdown(markdown_content)
  
  # Convert HTML to PDF
  file_name_without_ext = os.path.splitext(os.path.basename(file_path))[0]
  pdf_file_name = f"{file_name_without_ext}.pdf"
  pdf_output_path = os.path.join(_root_folder, pdf_file_name)
  
  print(f"Saving PDF to {pdf_output_path}...")
  HTML(string=html_content, base_url=_root_folder).write_pdf(pdf_output_path)
  
  total = round(time.time() - start_time, 3)
  print(f"Process completed in {total}s.")
  print(f"PDF documentation saved to: {pdf_output_path}")

# --- Main execution ---
if __name__ == "__main__":
    target_file = os.path.join(_root_folder, "file.py")
    if not os.path.exists(target_file):
        print(f"Error: Target file not found at {target_file}")
    else:
        run_generate_documentation_for_file(target_file)
