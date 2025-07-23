from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv  
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from tools import *


load_dotenv()

# This is the global variable to store document content
document_content = ""

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

toolset = return_all_implemented_tools()

super_agent = ChatOpenAI(model="gpt-4o").bind_tools(toolset)

with open("docs/agent_role.txt", "r") as file:
    role_prompt_text = file.read().strip()

def agent(state: AgentState) -> AgentState:
    System_prompt = SystemMessage(content = role_prompt_text)
    
    if not state["messages"]:
        user_input = "Please help me automate my software evolution process via tools."
        user_message = HumanMessage(content=user_input)

    else:
        user_input = input("\n User:")
        print(f"\n👤 USER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [System_prompt] + state["messages"] + [user_message] # type: ignore

    response = super_agent.invoke(all_messages)

    print(f"\n AI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f" USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")

    return {"messages": list(state["messages"]) + [user_message, response]}

def should_continue(state: AgentState) -> str:
    """  Check if the agent should continue or end based on the last AI message."""
    last_msg = state["messages"][-1]
    if isinstance(last_msg, AIMessage) and last_msg.additional_kwargs.get("finished") is True:
        return "end"
    return "continue"

def print_messages(messages):
    """Function I made to print the messages in a more readable format"""
    if not messages:
        return
    
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\n TOOL RESULT: {message.content}")

graph = StateGraph(AgentState)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(toolset))

graph.set_entry_point("agent")
graph.add_edge("agent", "tools")

graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue": "agent",
        "end": END,
    },
)

app = graph.compile()

def run_agent():
    print("Start the app")
    state = {"messages": []}

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    
    print("\n ===== DRAFTER FINISHED =====")

if __name__ == "__main__":
    run_agent()