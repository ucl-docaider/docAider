import os
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

azure_chat_completion_service = AzureChatCompletion(
  deployment_name=os.getenv("CHAT_DEPLOYMENT_NAME"),
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
  endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)