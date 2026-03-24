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
from wayflowcore.mcp import MCPTool, StdioTransport, enable_mcp_without_auth

from wayflowcore.models.openaiapitype import OpenAIAPIType
from wayflowcore.models import OllamaModel
from wayflowcore.tools import ClientTool
from wayflowcore.property import FloatProperty

llm = OpenAICompatibleModel(
    model_id="oca/gpt-5.1-codex",
    base_url="",
    api_key=os.environ['OCA_API_KEY'],
    api_type=OpenAIAPIType.RESPONSES,
)

# llm = OllamaModel(
#      model_id="qwen2:7b",
# )

AGENT_INSTRUCTIONS = """
You are a helpful coding agent.
""".strip()


 
# Add docs mcp to codex config
# codex mcp add wayflow_docs -- uv run --with mcp -- https://raw.githubusercontent.com/oracle/wayflow/refs/heads/main/examples/mcp/docs_mcp.py --base-docs-url https://oracle.github.io/wayflow/development
# Clone https://github.com/oracle/wayflow.git current dir 
# examples/mcp/docs_mcp.py path inside git repo
# cwd where wayflow repo cloned './wayflow'

#User query

#“Where is the MCP guide, and which transport should I use for a local subprocess server?”
#“Show me an existing WayFlow example that connects an agent to an MCP server.”
#“What can you browse in the WayFlow docs bundle?”
#“Before you write code, remind me what WayFlow means by an Agent.”







enable_mcp_without_auth()
docs_transport = StdioTransport(
    command="python",
    args=[
        "examples/mcp/docs_mcp.py",
        "--base-docs-url",
        "https://oracle.github.io/wayflow/development",
    ],
    cwd="./wayflow",
)

docs_tool = MCPTool(
    name="get_docs",
    client_transport=docs_transport,
)

assistant = Agent(
    llm=llm,
    tools=[docs_tool],
)



config = AgentSpecExporter().to_yaml(assistant)

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
