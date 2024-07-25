import os
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

azure_chat_completion_service = AzureChatCompletion(
  deployment_name=os.getenv("CHAT_DEPLOYMENT_NAME"),
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
  base_url=os.getenv("BASE_URL_OPENAI")
)

autogen_llm_config = dict(
  model=os.getenv("CHAT_DEPLOYMENT_NAME"),
  base_url=os.getenv("BASE_URL"),
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
  api_type=os.getenv("API_TYPE"),
  api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
  temperature=0
)