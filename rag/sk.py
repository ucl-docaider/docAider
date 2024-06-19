from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig

kernel = Kernel()

service_id="rag"
kernel.add_service(
  AzureChatCompletion(
    deployment_name="", # TODO: Get the deployment name
    endpoint="", # TODO: Get the endpoint
    api_key="" # TODO
  )
)
req_settings = kernel.get_prompt_execution_settings_from_service_id(service_id)
req_settings.max_tokens = 2000
req_settings.temperature = 0.7
req_settings.top_p = 0.8

prompt = """
1) A robot may not injure a human being or, through inaction,
allow a human being to come to harm.

2) A robot must obey orders given it by human beings except where
such orders would conflict with the First Law.

3) A robot must protect its own existence as long as such protection
does not conflict with the First or Second Law.

Give me the TLDR in exactly 5 words."""

# Prompt configuration
prompt_template_config = PromptTemplateConfig(
  template=prompt,
  name="tldr",
  template_format="semantic-kernel",
  execution_settings=req_settings,
)

# Register memory store using Azure AI Search 
# TODO

# Add a function with the prompt config to the kernel
function = kernel.add_function(
  function_name="tldr_function",
  plugin_name="tldr_plugin",
  prompt_template_config=prompt_template_config,
)

# Use `invoke` to get kernel response
result = kernel.invoke(function)
print(result)
