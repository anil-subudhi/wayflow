from wayflowcore.agent import Agent
from wayflowcore.agentspec import AgentSpecExporter
from wayflowcore.models import VllmModel
from wayflowcore.tools import tool
from wayflowcore.models import OllamaModel
from wayflowcore.executors.executionstatus import (
    FinishedStatus,
    UserMessageRequestStatus,
)

from wayflowcore.models.openaicompatiblemodel import OpenAICompatibleModel
import os
from wayflowcore.models.openaiapitype import OpenAIAPIType

# llm = VllmModel(
#     model_id="model-id",
#     host_port="VLLM_HOST_PORT",
# )

llm = OllamaModel(
     model_id="qwen2:7b",
)

# llm = OpenAICompatibleModel(
#     model_id="oca/gpt-5.1-codex",
#     base_url="",
#     api_key=os.environ['OCA_API_KEY'],
#     api_type=OpenAIAPIType.RESPONSES,
# )

@tool
def say_hello_tool() -> str:
    '''This tool returns "hello"'''
    return "hello Anil kumar"

@tool
def add_mumbers() -> str:
    """add two numbers"""
    return (
        "Starting long processing\n"

    )

agent = Agent(
    name="Simple Agent",
    llm=llm,
    tools=[say_hello_tool,add_mumbers]
)
config = AgentSpecExporter().to_json(agent)
#print(config)

# With a linear conversation
conversation = agent.start_conversation()
conversation.append_user_message("Greetings!")
status = conversation.execute()

if isinstance(status, UserMessageRequestStatus):
    assistant_reply = conversation.get_last_message()
    print(f"---\nAssistant >>> {assistant_reply.content}\n---")
else:
    print(f"Invalid execution status, expected UserMessageRequestStatus, received {type(status)}")





# from wayflowcore.agentspec import AgentSpecLoader
# TOOL_REGISTRY = {"say_hello_tool": say_hello_tool}
# loader = AgentSpecLoader(tool_registry=TOOL_REGISTRY)
# deser_agent = loader.load_json(config)
# print(deser_agent)


# import os
# from wayflowcore.agent import Agent
# from wayflowcore.agentspec import AgentSpecExporter, AgentSpecLoader
# from wayflowcore.executors.executionstatus import (
#     FinishedStatus,
#     UserMessageRequestStatus,
# )
# from wayflowcore.tools import tool
#
# from wayflowcore.models import VllmModel
# from wayflowcore.models.openaicompatiblemodel import OpenAICompatibleModel
#
# from wayflowcore.models.openaiapitype import OpenAIAPIType
#
# from wayflowcore.tools import ClientTool
# from wayflowcore.property import FloatProperty
#
# llm = OpenAICompatibleModel(
#     model_id="oca/gpt-5.1-codex",
#     base_url="",
#     api_key=os.environ['OCA_API_KEY'],
#     api_type=OpenAIAPIType.RESPONSES,
# )
#
# AGENT_INSTRUCTIONS = """
# You are a helpful coding agent.
# """.strip()



# @tool
# def say_hello_tool() -> str:
#     '''This tool returns "hello"'''
#     return "hello Anil"
#
# assistant = Agent(
#     name="Simple Agent",
#     custom_instruction=AGENT_INSTRUCTIONS,
#     llm=llm,
#     tools=[say_hello_tool]
# )
# config = AgentSpecExporter().to_yaml(assistant)
#
# inputs = {}
# conversation = assistant.start_conversation(inputs)
#
# while True:
#     status = conversation.execute()
#     if isinstance(status, FinishedStatus):
#         break
#     assistant_reply = conversation.get_last_message()
#     if assistant_reply is not None:
#         print("\nAssistant >>>", assistant_reply.content)
#     user_input = input("\nUser >>> ")
#     conversation.append_user_message(user_input)
