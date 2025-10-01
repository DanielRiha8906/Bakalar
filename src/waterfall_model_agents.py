from typing import Annotated, Sequence, TypedDict, Optional
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from tools import *
from datetime import datetime
import os

load_dotenv()

LOG_DIR = "src/logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "waterfall_model_log.txt")

def label_for_message(msg: BaseMessage, step_agent: Optional[str]) -> str:
        # infer agent for each message for accurate logs
        if isinstance(msg, ToolMessage):
            return "tools"
        if isinstance(msg, HumanMessage):
            return "client"
        # AIMessage -> whoever the current node is
        return step_agent or "unknown"

def append_log(log: str):
    time_stamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time_stamp}]: {log}\n")





class MultiAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next_step: Optional[str]  # used for routing between agents
    agent: Optional[str]  # current agent name - for logging/debugging

def _recent(state: MultiAgentState, k: int = 40) -> list[BaseMessage]:
    msgs = list(state.get("messages", []))
    if not msgs:
        return []
    cut = msgs[-k:]

    def fix_leading_tool(cut_list):
        if not cut_list or not isinstance(cut_list[0], ToolMessage):
            return cut_list
        start_idx = len(msgs) - len(cut_list)
        i = start_idx - 1
        while i >= 0:
            m = msgs[i]
            if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
                return msgs[i:]
            i -= 1
        tmp = cut_list[:]
        while tmp and isinstance(tmp[0], ToolMessage):
            tmp = tmp[1:]
        return tmp

    cut = fix_leading_tool(cut)

    if cut and isinstance(cut[-1], AIMessage) and getattr(cut[-1], "tool_calls", None):
        end_idx = len(msgs)
        slice_start = end_idx - len(cut)
        after_last = slice_start + len(cut)
        if after_last >= len(msgs) or not isinstance(msgs[after_last], ToolMessage):
            cut = cut[:-1]

    return cut


def _sanitize_for_openai(system_msg: SystemMessage, recent: list[BaseMessage], full_history: list[BaseMessage]) -> list[BaseMessage]:
    prompt = [system_msg]

    while recent and isinstance(recent[0], ToolMessage):
        idx = full_history.index(recent[0])
        j = idx - 1
        found = False
        while j >= 0:
            m = full_history[j]
            if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
                recent = full_history[j: full_history.index(recent[0]) + len(recent)]
                found = True
                break
            j -= 1
        if not found:
            recent = recent[1:]

    cleaned = []
    for m in recent:
        if isinstance(m, ToolMessage):
            if cleaned and isinstance(cleaned[-1], AIMessage) and getattr(cleaned[-1], "tool_calls", None):
                cleaned.append(m)  
            else:
                cleaned.append(m)  
        else:
            cleaned.append(m)

    # don't end on tool_calls
    if cleaned and isinstance(cleaned[-1], AIMessage) and getattr(cleaned[-1], "tool_calls", None):
        cleaned = cleaned[:-1]

    return prompt + cleaned



toolset = return_all_implemented_tools()
super_agent = ChatOpenAI(model="gpt-4o-mini").bind_tools(toolset)


def step_router(state: MultiAgentState) -> str:
    return state.get("next_step") or "end"


def client_node(state: MultiAgentState) -> MultiAgentState:
    issue = input("\nUser: Describe the issue to solve: ")
    return {
        "messages": [HumanMessage(content=issue)],
        "next_step": "analyst",
        "agent": "client",
    }


def analyst_agent(state: MultiAgentState) -> MultiAgentState:
    state["agent"] = "analyst"
    print("[ANALYST] Processing issue...")
    system_msg = SystemMessage(content=
        "Role: Analyst.\n"
        "Goal: Extract concrete technical requirements and constraints to solve the users request.\n"
        "Sources: The user message and (if referenced by prior messages) the GitHub issue text that tools returned.\n"
        "Hard rules:\n"
        "- When you DO NOT KNOW the username of the user, use get_me tool\n"
        "- Do NOT call any tools, that would modify the codebase. Only exploratory tools are allowsed.\n"
        "- Do NOT ask the user to confirm obvious next steps; decide and proceed.\n"
        "Output:\n"
        "- A concise bullet list of requirements.\n"
        "- Any uncertainties with a recommended assumption.\n"
        "- The single next role to route to: 'architect'.")
    recent = _recent(state)
    prompt = _sanitize_for_openai(system_msg, recent, list(state.get("messages", [])))
    response = super_agent.invoke(prompt)
    state["messages"] = [*state["messages"], response]
    state["next_step"] = "analyst_tools" if getattr(response, "tool_calls", None) else "architect"
    return state


def architect_agent(state: MultiAgentState) -> MultiAgentState:
    state["agent"] = "architect"
    print("[ARCHITECT] Finding affected components...")
    system_msg = SystemMessage(content=
        "Role: Architect.\n"
        "Goal: Turn requirements into an execution plan and file-level changes.\n"
        "Hard rules:\n"
        "- Do NOT call tools that would modify the codebase.\n"
        "- Assume repository access will be performed by the Programmer/Tester.\n"
        "Output:\n"
        "- A numbered task list for the Programmer (files to edit/create, branches to use, test files to add).\n"
        "- A numbered task list for the Tester (what to verify, which workflow to expect).\n"
        "- The single next role to route to: 'programmer'.")
    recent = _recent(state)
    prompt = _sanitize_for_openai(system_msg, recent, list(state.get("messages", [])))
    response = super_agent.invoke(prompt)
    state["messages"] = [*state["messages"], response]
    state["next_step"] = "architect_tools" if getattr(response, "tool_calls", None) else "programmer"
    return state


def programmer_agent(state: MultiAgentState) -> MultiAgentState:
    state["agent"] = "programmer"
    print("[PROGRAMMER] Writing code change...")
    system_msg = SystemMessage(content=
        "Role: Programmer.\n"
        "Goal: Use the available repo tools to apply the code changes described by the Architect.\n"
        "Operating rules:\n"
        "- If a feature branch is requested but missing, create it from 'main'.\n"
        "- All edits MUST be committed to that feature branch (do not touch 'main').\n"
        "- Use idempotent writes (create_or_update_file with explicit 'branch').\n"
        "- If paths are unknown, list repo contents first, then proceed.\n"
        "- Do NOT ask the user for confirmation.\n"
        "- DO NOT run GitHub Actions yourself.\n"
        "- DO NOT Create tests yourself, that is what Tester is for.\n"
        "Output:\n"
        "- Brief summary of edits/commits performed.\n"
        "- If further edits are needed, perform them (using tools) before yielding.\n"
        "- If no more code changes are needed, set next step to 'tester'.")
    recent = _recent(state)
    prompt = _sanitize_for_openai(system_msg, recent, list(state.get("messages", [])))
    response = super_agent.invoke(prompt)
    state["messages"] = [*state["messages"], response]
    state["next_step"] = "programmer_tools" if getattr(response, "tool_calls", None) else "tester"
    return state


def tester_agent(state: MultiAgentState) -> MultiAgentState:
    state["agent"] = "tester"
    print("[TESTER] Running tests...")
    system_msg = SystemMessage(content=(
    "Role: Tester.\n"
    "Goal: Ensure automated tests exist and are executed in CI, then report pass/fail.\n"
    "Operating rules (perform with tools):\n"
    "1) Ensure tests exist for affected files. If missing, create them under the 'tests/' folder "
    "   (e.g., 'tests/test_calculator.py'). If a test file exists at repo root, move it into 'tests/'.\n"
    "2a) Ensure CI workflow exists at '.github/workflows/python-tests.yml' running 'pytest -q' on push/PR.\n"
    "2b) If 'list_workflow_runs' returns 404 for that path, CREATE the workflow via create_or_update_file "
    "    (must include a 'message' field), then SKIP listing runs this turn and set next_step='end'.\n"
    "3) Commit changes to the current feature branch (NOT 'main').\n"
    "4) Do NOT ask the user for confirmation.\n"
    "5) First explain your plan.\n"
    "6) All tests must live under 'tests/'.\n"
    "7) In case you would create or update anything. It must be done in a feature branch. NEVER ON MAIN.\n"
    "Output:\n"
    "- What files you created/updated and on which branch.\n"
    "- CI run status if available; if newly created, instruct how to check the run.\n"
    "- If failing, list failing tests and propose fixes.\n"
))
    recent = _recent(state)
    prompt = _sanitize_for_openai(system_msg, recent, list(state.get("messages", [])))
    response = super_agent.invoke(prompt)
    state["messages"] = [*state["messages"], response]
    state["next_step"] = "tester_tools" if getattr(response, "tool_calls", None) else "end"
    return state


graph = StateGraph(MultiAgentState)

# Nodes
graph.add_node("client", client_node)
graph.add_node("analyst", analyst_agent)
graph.add_node("architect", architect_agent)
graph.add_node("programmer", programmer_agent)
graph.add_node("tester", tester_agent)
graph.add_node("done", lambda state: state)

tool_node = ToolNode(toolset)
graph.add_node("tools", tool_node)

graph.set_entry_point("client")

graph.add_conditional_edges("client", step_router, {
    "analyst": "analyst",
})

graph.add_conditional_edges("analyst", step_router, {
    "analyst_tools": "tools",
    "architect": "architect",
})

graph.add_conditional_edges("architect", step_router, {
    "architect_tools": "tools",
    "programmer": "programmer",
})

graph.add_conditional_edges("programmer", step_router, {
    "programmer_tools": "tools",
    "tester": "tester",
})

graph.add_conditional_edges("tester", step_router, {
    "tester_tools": "tools",
    "end": "done",
})

graph.add_conditional_edges("tools", step_router, {
    "analyst_tools": "analyst",
    "architect_tools": "architect",
    "programmer_tools": "programmer",
    "tester_tools": "tester",
    "end": "done",
})

app = graph.compile()


def run_agent():
    print("\n=== STARTING MULTI-AGENT WORKFLOW ===")
    state: MultiAgentState = {"messages": [], "next_step": None, "agent": None}

    for step in app.stream(state, stream_mode="values", config={"recursion_limit": 60}):
        step_agent = step.get("agent")  # set by each node above
        if "messages" in step:
            for m in step["messages"][-2:]:
                who = label_for_message(m, step_agent)
                line = f"[{who} | {type(m).__name__}] {m.content}"
                print(line)
                append_log(line)

    print("\n=== WORKFLOW COMPLETE ===")


if __name__ == "__main__":
    run_agent()
 