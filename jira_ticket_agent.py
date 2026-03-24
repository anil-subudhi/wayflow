from pyagentspec.llms.openaicompatibleconfig import OpenAIAPIType
from wayflowcore.models.openaicompatiblemodel import OpenAICompatibleModel
import os
#from wayflowcore.models.openaiapitype import OpenAIAPIType
from pyagentspec.llms import OpenAiCompatibleConfig
from pyagentspec.llms import OllamaConfig
from pyagentspec.agent import Agent
from pyagentspec.property import StringProperty
from pyagentspec.tools import ServerTool
from pyagentspec.serialization import AgentSpecSerializer
from wayflowcore.agentspec import AgentSpecLoader as WayFlowLoader
from wayflowcore.agent import Agent as RuntimeAgent
from wayflowcore.executors.executionstatus import UserMessageRequestStatus
from wayflowcore.agentspec import AgentSpecLoader

# llm_config = OllamaConfig(
#     name="ollama-llm",
#     model_id="qwen2:7b",
#     url="url/to/ollama_model" # e.g. localhost:11434
# )

llm_config = OpenAiCompatibleConfig(
    name="ocimodel",
    model_id="oca/gpt-5.1-codex",
    url=""
    api_key=os.environ['OCA_API_KEY'],
    api_type=OpenAIAPIType.RESPONSES,
)

get_context_tool = ServerTool(
    name="get_context",
    description="Return a context summary for a Jira incident.",
    inputs=[StringProperty(title="jira_issue_id")],
    outputs=[StringProperty(title="incident_summary")]
)

def get_context(jira_issue_id: str) -> str:
   """Return a context summary for a Jira incident."""
   if jira_issue_id == "INC-12345":
      return "Payments API latency incident in us-west-1 during 2025-10-08T14:20Z–14:40Z."
   if jira_issue_id == "INC-56789":
      return "Inventory service 5xx spike in eu-frankfurt-1 during 2025-10-08T09:00Z–09:15Z."
   return f"No context available for {jira_issue_id}."

# agent_config = Agent(
#    name="Operation Assistant Agent",
#    description="Agent equipped with tools to assist with operation incidents",
#    llm_config=llm_config,
#    tools=[get_context_tool],
#    system_prompt="You are an Operations Agent. Use the tools to solve user requests."
# )


# tool_registry = {"get_context": get_context}
# agent = AgentSpecLoader(tool_registry=tool_registry).load_component(agent_config)

# conversation = agent.start_conversation()
# conversation.append_user_message("Please help with the ticket INC-12345")
# status = conversation.execute()
# last_agent_message = conversation.get_last_message()
# print(last_agent_message.content)
# There was a Payments API latency incident in us-west-1 during 2025-10-08T14:20Z–14:40Z# Is there anything else I can help you with regarding ticket INC-12345?


read_jira_ticket_tool = ServerTool(
    name="read_jira_ticket",
    description="Return a plain-text summary of the Jira incident.",
    inputs=[
        StringProperty(title="jira_issue_id", description='The Jira issue key, e.g., "INC-12345"')
    ],
    outputs=[
        StringProperty(
            title="incident_summary", 
            description="A human-readable incident summary including scope, runbook, and time window."
        )
    ]
)


def read_jira_ticket(jira_issue_id: str) -> str:
    """Return a plain-text summary of the Jira incident."""
    if jira_issue_id == "INC-12345":
        return (
            "Incident INC-12345\n"
            "Summary: Elevated latency on Payments API in us-west-1\n"
            "Detected by: CloudWatch Alarm cw:payments-latency-high\n"
            "Impact: 5xx/latency spikes for checkout\n"
            "Scope: Project=payments, Fleet=payments-api, Compartment=prod, Region=us-west-1\n"
            "Suspected window: 2025-10-08T14:20Z to 2025-10-08T14:40Z\n"
            "Suggested runbook: payments-latency-runbook\n"
            "Related deployments: deploy-2025-10-08-1330Z\n"
            "Notes: Started after feature flag payments.v2.retry=true was enabled."
        )
    if jira_issue_id == "INC-56789":
        return (
            "Incident INC-56789\n"
            "Summary: Error rate on Inventory service in eu-frankfurt-1\n"
            "Detected by: Alarm cw:inventory-5xx\n"
            "Impact: GET /inventory/{sku} returning 500s\n"
            "Scope: Project=inventory, Fleet=inventory-service, Compartment=prod, Region=eu-frankfurt-1\n"
            "Suspected window: 2025-10-08T09:00Z to 2025-10-08T09:15Z\n"
            "Suggested runbook: inventory-5xx-triage\n"
            "Notes: Recent DB maintenance in compartment prod-db."
        )
    return "Ticket not found"


read_runbook_tool = ServerTool(
    name="read_runbook",
    description="Return the markdown content of a runbook by name.",
    inputs=[StringProperty(title="runbook_name", description="The canonical runbook name.")],
    outputs=[StringProperty(title="runbook_markdown", description="Markdown content of the runbook.")]
)

def read_runbook(runbook_name: str) -> str:
    """Return the markdown content of a runbook by name."""
    if runbook_name == "payments-latency-runbook":
        return (
            "# Payments API Latency Runbook\n"
            "Preconditions:\n"
            "- Alarm: cw:payments-latency-high\n"
            "- Region: us-west-1\n"
            "Steps:\n"
            "1. Verify alarm status.\n"
            "2. Check logs for timeouts and thread pool saturation:\n"
            "   - project=payments, fleet=payments-api, level>=WARN\n"
            "3. Roll back recent feature flags if correlated.\n"
            "4. If DB timeouts present, increase pool size by 20% and purge hot caches.\n"
            "Validation:\n"
            "- P95 latency < 300ms for 10 minutes.\n"
            "Escalation: page on-call db and network if persists > 30 min."
        )
    if runbook_name == "inventory-5xx-triage":
        return (
            "# Inventory 5xx Triage\n"
            "Steps:\n"
            "1. Confirm cw:inventory-5xx alarm.\n"
            "2. Check error logs for NullPointerException or DB connection errors.\n"
            "3. If DB errors, fail over read replica.\n"
            "4. If code exceptions, roll back latest deploy.\n"
            "Validation: 5xx < 1% for 15 min."
        )
    return f"# Runbook not found: {runbook_name}"


get_alarm_status_tool = ServerTool(
    name="get_alarm_status",
    description="Return the current status of an alarm: 'firing' or 'not firing'.",
    inputs=[
        StringProperty(title="region", description="Cloud region (e.g., 'us-west-1', 'eu-frankfurt-1')"), 
        StringProperty(title="alarm_id", description="Alarm identifier (e.g., 'cw:payments-latency-high')")
    ],
    outputs=[StringProperty(title="alarm_status", description="'firing' or 'not firing'")]
)

def get_alarm_status(region: str, alarm_id: str) -> str:
    """Return the current status of an alarm: 'firing' or 'not firing'."""
    if region == "us-west-1" and alarm_id == "cw:payments-latency-high":
        return "firing"
    if region == "eu-frankfurt-1" and alarm_id == "cw:inventory-5xx":
        return "not firing"
    return "not firing"


read_logs_tool = ServerTool(
    name="read_logs",
    description="Return log lines for the given filters as a single plain string.",
    inputs=[
        StringProperty(title="from_project", description="Owning project (e.g., 'payments', 'inventory')"),
        StringProperty(title="from_fleet", description="Service/fleet name"),
        StringProperty(title="from_compartment", description="Environment/compartment (e.g., 'prod')"),
        StringProperty(title="from_region", description="Cloud region"),
        StringProperty(title="log_level", description="Minimum log level (string)"),
        StringProperty(title="start_ts", description="ISO8601 start timestamp"),
        StringProperty(title="end_ts", description="ISO8601 end timestamp"),
    ],
    outputs=[StringProperty(title="log_lines", description="Concatenated log lines or a friendly 'no logs' message.")]
)

def read_logs(
    from_project: str,
    from_fleet: str,
    from_compartment: str,
    from_region: str,
    log_level: str,
    start_ts: str,
    end_ts: str,
) -> str:
    """Return log lines for the given filters as a single plain string."""
    # Scenario 1: Payments latency WARN logs
    if (
        from_project == "payments"
        and from_fleet == "payments-api"
        and from_compartment == "prod"
        and from_region == "us-west-1"
        and log_level.upper() == "WARN"
        and start_ts == "2025-10-08T14:20:00Z"
        and end_ts == "2025-10-08T14:40:00Z"
    ):
        return (
            "2025-10-08T14:22:11Z WARN [payments-api] HTTP timeout to db-primary.usw1:5432 (p95=1200ms)\n"
            "2025-10-08T14:23:05Z WARN [payments-api] ThreadPool saturation: active=200 queued=53 max=200\n"
            "2025-10-08T14:24:49Z WARN [payments-api] Downstream gateway timeout /charge POST traceId=abc123\n"
            "2025-10-08T14:26:12Z WARN [payments-api] Retrying request due to TimeoutException component=db-client"
        )

    # Scenario 2: Inventory ERROR logs
    if (
        from_project == "inventory"
        and from_fleet == "inventory-service"
        and from_compartment == "prod"
        and from_region == "eu-frankfurt-1"
        and log_level.upper() == "ERROR"
        and start_ts == "2025-10-08T09:00:00Z"
        and end_ts == "2025-10-08T09:15:00Z"
    ):
        return (
            "2025-10-08T09:03:44Z ERROR [inventory-service] SQLSTATE 08001 connection failure to db-replica-1\n"
            "2025-10-08T09:04:10Z ERROR [inventory-service] SQLSTATE 08001 connection failure to db-replica-1\n"
            "2025-10-08T09:07:29Z ERROR [inventory-service] NullPointerException at InventoryController.java:142"
        )

    return "No logs matched the provided filters."

CUSTOM_INSTRUCTIONS = """
You are an LLM-based operations assistant. You have four tools available:
read_jira_ticket, read_runbook, get_alarm_status, read_logs

Investigation flow (starting with a Jira ID)
1) Retrieve ticket
   - Call read_jira_ticket(jira_issue_id).
   - If the ticket is “not found,” ask the user to confirm the ID.

2) Load runbook
   - If “Suggested runbook” is present, call read_runbook(runbook_name).
   - Extract key steps and validation criteria.

3) Verify alarm status
   - If alarm_id and region are known, call get_alarm_status(region, alarm_id).
   - Record “firing” vs “not firing” as part of the state.

4) Inspect logs
   - Determine sensible parameters from the ticket, call read_logs with those fields.
   - If logs return “No logs matched,” consider adjusting the fields.
   - Summarize key patterns, errors, and timestamps from logs.

5) Form a hypothesis and recommended actions
   - Synthesize alarm status, logs, runbook guidance, and notes from the ticket.
   - Provide a clear, probable cause hypothesis with confidence qualifiers.
   - Recommend next steps aligned to the runbook.

6) Report results in a structured format
Use this output template:
- Incident: <jira_issue_id>
- Summary: <one-liner from Jira or your concise rewrite>
- Scope: Project=<project>, Fleet=<fleet>, Compartment=<compartment>, Region=<region>
- Time window: <start_ts> to <end_ts> (from ticket or adjusted)
- Alarm: <alarm_id> — Status: <firing|not firing|unknown>
- Evidence:
- Ticket highlights: <key notes, deployments, flags>
- Logs (top 3-6 lines or patterns): <short bullets with timestamps and error types>
- Runbook: <name> — Key steps considered: <bulleted list of most relevant steps>
- Hypothesis: <probable cause and rationale>
- Recommended actions: <ordered list; include rollback/failover/tuning/monitoring>
- Validation: <what success looks like (e.g., P95 < threshold for X min)>
- Open questions/next checks: <only if needed>
- Artifacts: <any identifiers: deployment IDs, feature flags, trace IDs seen in logs>
""".strip()


agent_config = Agent(
    name="Operation_Assistant_Agent",
    description="Agent equipped with tools to assist with operation incidents",
    llm_config=llm_config,
    tools=[read_jira_ticket_tool, read_logs_tool, read_runbook_tool, get_alarm_status_tool],
    system_prompt=CUSTOM_INSTRUCTIONS
)


serialized_agent = AgentSpecSerializer().to_json(agent_config)

 
# LOADING agent config using wayflow framework


tool_registry = {
    "read_jira_ticket": read_jira_ticket,
    "read_logs": read_logs,
    "read_runbook": read_runbook,
    "get_alarm_status": get_alarm_status,
}

#agent: RuntimeAgent = WayFlowLoader(tool_registry=tool_registry).load_json(serialized_agent)
agent = AgentSpecLoader(tool_registry=tool_registry).load_component(agent_config)



conversation = agent.start_conversation()

while True:
   status = conversation.execute()
   if not isinstance(status, UserMessageRequestStatus):
      break
   assistant_reply = conversation.get_last_message()
   if assistant_reply is not None:
      print("\nAssistant >>>", assistant_reply.content)
   user_input = input("\nUser >>> ")
   conversation.append_user_message(user_input)