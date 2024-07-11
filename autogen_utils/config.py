from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the variables from the environment
llm_config = dict(
    model=os.getenv("MODEL"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
    api_type=os.getenv("API_TYPE"),
    api_version=os.getenv("API_VERSION"),
)