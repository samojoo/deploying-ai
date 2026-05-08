import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt.tool_node import ToolNode, tools_condition

from assignment_chat.prompts import return_instructions
from assignment_chat.tools_compare import compare_tickers
from assignment_chat.tools_market_knowledge import search_market_knowledge
from assignment_chat.tools_prices import get_latest_prices

load_dotenv("05_src/.secrets")
load_dotenv(".secrets")

tools = [get_latest_prices, search_market_knowledge, compare_tickers]
instructions = return_instructions()

chat_agent = init_chat_model(
    "openai:gpt-4o-mini",
    temperature=0.2,
    base_url="https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
    api_key="any value",
    default_headers={"x-api-key": os.getenv("API_GATEWAY_KEY")},
)


def call_model(state: MessagesState):
    """Let the LLM decide whether to call one of the stock-market tools."""
    response = chat_agent.bind_tools(tools).invoke(
        [SystemMessage(content=instructions)] + state["messages"]
    )
    return {"messages": [response]}


def get_graph():
    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_node(ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")
    return builder.compile()
