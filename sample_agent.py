import os
from wayflowcore.agent import Agent
from wayflowcore.agentspec import AgentSpecExporter, AgentSpecLoader
from wayflowcore.executors.executionstatus import (
    FinishedStatus,
    UserMessageRequestStatus,
)
from wayflowcore.tools import tool

from wayflowcore.models import VllmModel
from wayflowcore.models.openaicompatiblemodel import OpenAICompatibleModel

from wayflowcore.models.openaiapitype import OpenAIAPIType

from wayflowcore.tools import ClientTool
from wayflowcore.property import FloatProperty

llm = OpenAICompatibleModel(
    model_id="oca/gpt-5.1-codex",
    base_url="model_url",
    api_key=os.environ['OCA_API_KEY'],
    api_type=OpenAIAPIType.RESPONSES,
)

AGENT_INSTRUCTIONS = """
You are a helpful coding agent.
""".strip()

def add_tool(arg1, arg2):
   printf(">>>>>>>>>ADDING TOOL>>>>>>>>>>>>")
   return arg1 + arg2

addition_client_tool = ClientTool(
   name="add_numbers",
   description="Simply adds two numbers",
   input_descriptors=[
        FloatProperty(name="a", description="the first number", default_value=0),
        FloatProperty(name="b", description="the second number"),
   ],
   output_descriptors=[FloatProperty()]
)

assistant = Agent(
    custom_instruction=AGENT_INSTRUCTIONS,
    tools=[addition_client_tool],  # this is a decorated python function (Server tool in this example)
    llm=llm,  # the LLM object we created above
)

inputs = {}
conversation = assistant.start_conversation(inputs)

while True:
    status = conversation.execute()
    if isinstance(status, FinishedStatus):
        break
    assistant_reply = conversation.get_last_message()
    if assistant_reply is not None:
        print("\nAssistant >>>", assistant_reply.content)
    user_input = input("\nUser >>> ")
    conversation.append_user_message(user_input)
