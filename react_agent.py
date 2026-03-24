from datetime import datetime

from wayflowcore.contextproviders import ToolContextProvider
from wayflowcore.tools import tool
from wayflowcore.models.openaicompatiblemodel import OpenAICompatibleModel
import os
from wayflowcore.models.openaiapitype import OpenAIAPIType
from wayflowcore.agent import Agent

@tool
def get_current_time() -> str:
    """Tool that gets the current time"""
    return datetime.now().strftime("%d, %B %Y, %I:%M %p")

time_provider = ToolContextProvider(tool=get_current_time, output_name="current_time")

llm = OpenAICompatibleModel(
    model_id="oca/gpt-5.1-codex",
    base_url="",
    api_key=os.environ['OCA_API_KEY'],
    api_type=OpenAIAPIType.RESPONSES,
)

agent = Agent(
    llm=llm,
    custom_instruction="""Your a helpful writing assistant. Answer the user's questions about article writing.
It's currently {{current_time}}.""",
    initial_message=None,
    context_providers=[time_provider],
)

conversation = agent.start_conversation()
conversation.execute()
last_message = conversation.get_last_message()
print(last_message.content if last_message else "No message")
# I'm here to assist you with any article writing-related questions or concerns. What do you need help with today?