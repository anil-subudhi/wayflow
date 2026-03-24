import os
from wayflowcore.agent import Agent
from wayflowcore.agentspec import AgentSpecExporter, AgentSpecLoader
from wayflowcore.executors.executionstatus import (
    FinishedStatus,
    UserMessageRequestStatus,
)
from wayflowcore.tools import tool
import anyio
from wayflowcore.models import VllmModel
from wayflowcore.models.openaicompatiblemodel import OpenAICompatibleModel

from wayflowcore.models.openaiapitype import OpenAIAPIType

llm = OpenAICompatibleModel(
    model_id="oca/gpt-5.1-codex",
    base_url="",
    api_key=os.environ['OCA_API_KEY'],
    api_type=OpenAIAPIType.RESPONSES,
)

# %%[markdown]
## Single async generation

# %%


from wayflowcore.agent import Agent

agent = Agent(
    llm=llm,
    custom_instruction="You are a helpful assistant.",
)
conv = agent.start_conversation()
conv.append_user_message("Who is the CEO of Oracle?")
out = anyio.run(conv.execute_async)

print(out.message.contents[0])

# AGENT_INSTRUCTIONS = """
# You are a helpful coding agent.
# """.strip()

# assistant = Agent(
#     custom_instruction=AGENT_INSTRUCTIONS,
#     tools=[],  # this is a decorated python function (Server tool in this example)
#     llm=llm,  # the LLM object we created above
# )

# inputs = {}
# conversation = assistant.start_conversation(inputs)

# while True:
#     status = conversation.execute()
#     if isinstance(status, FinishedStatus):
#         break
#     assistant_reply = conversation.get_last_message()
#     if assistant_reply is not None:
#         print("\nAssistant >>>", assistant_reply.content)
#     user_input = input("\nUser >>> ")
#     conversation.append_user_message(user_input)
