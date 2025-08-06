from typing import Annotated, Sequence, TypedDict, Optional
from dotenv import load_dotenv  
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from tools import *

load_dotenv()

class MultiAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next_step: Optional[str]  # used for routing between agents

toolset = return_all_implemented_tools()
super_agent = ChatOpenAI(model="gpt-4o").bind_tools(toolset)

def step_router(state: MultiAgentState) -> str:
    return state.get("next_step") or "end"

def client_node(state: MultiAgentState) -> MultiAgentState:
    issue = input("\nUser: Describe the issue to solve: ")
    return {
        "messages": [HumanMessage(content=issue)],
        "next_step": "analyst"
    }

def analyst_agent(state: MultiAgentState) -> MultiAgentState:
    print("[ANALYST] Processing issue...")
    system_msg = SystemMessage(content="You are an Analyst. Extract structured technical requirements from the user input.")
    recent = list(state["messages"])[-5:]
    response = super_agent.invoke([system_msg] + recent)
    state["messages"] = list(state["messages"]) + [response]
    state["next_step"] = "architect"
    return state

def architect_agent(state: MultiAgentState) -> MultiAgentState:
    print("[ARCHITECT] Finding affected components...")
    system_msg = SystemMessage(content="You are an Architect. Based on the requirements, identify affected code areas and define tasks for the programmer.")
    recent = list(state["messages"])[-5:]
    response = super_agent.invoke([system_msg] + recent)
    state["messages"] = list(state["messages"]) + [response]
    state["next_step"] = "programmer"
    return state

def programmer_agent(state: MultiAgentState) -> MultiAgentState:
    print("[PROGRAMMER] Writing code change...")
    system_msg = SystemMessage(content="You are a Programmer. Write the code required to implement the architectural tasks.")
    recent = list(state["messages"])[-5:]
    response = super_agent.invoke([system_msg] + recent)
    state["messages"] = list(state["messages"]) + [response]
    state["next_step"] = "tester"
    return state

def tester_agent(state: MultiAgentState) -> MultiAgentState:
    print("[TESTER] Running tests...")
    system_msg = SystemMessage(content="You are a Tester. Write and run tests to validate the implementation. If tests fail, return it to the programmer.")
    recent = list(state["messages"])[-5:]
    response = super_agent.invoke([system_msg] + recent)
    state["messages"] = list(state["messages"]) + [response]
    state["next_step"] = "end"  # You could make this dynamic later
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

# Entry
graph.set_entry_point("client")

graph.add_conditional_edges("client", step_router, {"analyst": "analyst"})
graph.add_edge("analyst", "tools")
graph.add_edge("architect", "tools")
graph.add_edge("programmer", "tools")
graph.add_edge("tester", "tools")

graph.add_conditional_edges("tools", step_router, {
    "client": "client",
    "architect": "architect",
    "programmer": "programmer",
    "tester": "tester",
    "end": "done"
})

app = graph.compile()

def run_agent():
    print("\n=== STARTING MULTI-AGENT WORKFLOW ===")
    state: MultiAgentState = {
        "messages": [],
        "next_step": None
    }

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            for m in step["messages"][-2:]:
                print(f"[{type(m).__name__}] {m.content}")

    print("\n=== WORKFLOW COMPLETE ===")

if __name__ == "__main__":
    run_agent()
