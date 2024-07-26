from autogen import ConversableAgent
import azure_openai_settings as ai_service_settings
from repo_agents.prompt import UPDATE_REVIEW_PROMPT

"""
Multi-agent conversation pattern: sequential chats
Assistant agent: creates response for the given prompt
Review agent: performs self-check on the documentation content
Agent manager: is the mediator of the conversation
"""

assistant_agent = ConversableAgent(
  name="assistant_agent",
  system_message="You are an AI assistant for managing documentation for the code.",
  llm_config=ai_service_settings.autogen_llm_config,
  human_input_mode="NEVER"
)

review_agent = ConversableAgent(
  name="review_agent",
  system_message="You are a documentation reviewer who can check the quality of the generated documentation and improve it if necessary.",
  llm_config=ai_service_settings.autogen_llm_config,
  human_input_mode="NEVER"
)

agent_manager = ConversableAgent(
  name="agent_manager",
  llm_config=False,
  human_input_mode="NEVER"
)

def multi_agent_documentation_update(prompt) -> str:
  chat_result = agent_manager.initiate_chats(
    [
      {
        "recipient": assistant_agent,
        # Context: Prompt
        # Carryover: None
        "message": prompt,
        "max_turns": 1,
        "summary_method": "last_msg",
      },
      {
        "recipient": review_agent,
        # Context: None (You can add additional context)
        # Carryover: The output of the assistant agent
        "message": UPDATE_REVIEW_PROMPT,
        "max_turns": 1,
        "summary_method": "reflection_with_llm",
      }
    ]
  )
  return chat_result[1].chat_history[-1]["content"]