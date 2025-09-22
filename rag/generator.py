import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from repo_documentation.prompt import DOCUMENTATION_PROMPT
from exceptions import DocGenByKernelFailed

load_dotenv(dotenv_path="../.env")

class DocumentationGenerator():
  """
  This class uses LangChain for generating documentation for the code.
  """
  def __init__(self):
    """
    Initialize a new instance of the DocumentationGenerator class
    """
    self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0, google_api_key=os.getenv("GEMINI_API_KEY"))
    self.prompt_template = ChatPromptTemplate.from_template(DOCUMENTATION_PROMPT)
    self.chain = self.prompt_template | self.llm
    self.prompt = ""


  async def generate_documentation(self, file_path, file_content, root_folder, additional_docs) -> str:
    """
    This function generates documentation for code.

    Args:
      file_path: the name of the source file.
      file_content: the source code.
      root_folder: the root folder of the repository.
      additional_docs: the additional docs.
    
    Returns:
      LLM-generated documentation in string
    """
    file_name = os.path.basename(file_path)
    
    try:
      response = await self.chain.ainvoke({
          "file_name": file_name,
          "file_content": file_content,
          "root_folder": root_folder,
          "additional_docs": additional_docs
      })

      documentation = response.content
      print(f"Documentation generated for {file_name}.")
      return documentation
    except Exception as e:
      raise DocGenByKernelFailed(f"The generation for {file_name} failed: {e}")
