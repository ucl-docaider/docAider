from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(dotenv_path='../.env')

# Get the variables from the environment
llm_config = dict(
    model=os.getenv("CHAT_DEPLOYMENT_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_type=os.getenv("API_TYPE"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)