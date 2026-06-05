import os
import json
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_ollama import ChatOllama, OllamaLLM
from app.agent.tools import ALL_TOOLS
import operator

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "llm_config.json")

# Cache config to avoid reading file every time
_config_cache = None

def load_config() -> dict:
    global _config_cache
    if _config_cache is None:
        with open(CONFIG_PATH) as f:
            _config_cache = json.load(f)
    return _config_cache


# ── State ──────────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


# Cache LLM instance
_llm_cache = None

# ── LLM selection ──────────────────────────────────────────────────────────
def get_llm():
    global _llm_cache
    if _llm_cache is not None:
        return _llm_cache
        
    cfg = load_config()
    provider = cfg["provider"]
    model = cfg["model"]
    temp = cfg.get("temperature", 0.7)

    if provider == "ollama":
        _llm_cache = ChatOllama(
            model=model,
            temperature=temp,
        ).bind_tools(ALL_TOOLS)

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        openai_cfg = cfg.get("openai", {})
        api_key = os.getenv(openai_cfg.get("api_key_env", "OPENAI_API_KEY"))
        base_url = os.getenv(openai_cfg.get("base_url_env", "OPENAI_BASE_URL"))
        
        kwargs = {
            "model": model,
            "openai_api_key": api_key,
            "temperature": temp,
        }
        if base_url:
            kwargs["base_url"] = base_url
            
        _llm_cache = ChatOpenAI(**kwargs).bind_tools(ALL_TOOLS)

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        anthropic_cfg = cfg.get("anthropic", {})
        api_key = os.getenv(anthropic_cfg.get("api_key_env", "ANTHROPIC_API_KEY"))
        
        _llm_cache = ChatAnthropic(
            model=model,
            anthropic_api_key=api_key,
            temperature=temp,
        ).bind_tools(ALL_TOOLS)

    else:
        raise ValueError(cfg["error_messages"]["unsupported_provider"].format(provider=provider))
    
    return _llm_cache


# ── Nodes ──────────────────────────────────────────────────────────────────
def agent_node(state: AgentState):
    cfg = load_config()
    llm = get_llm()
    messages = [SystemMessage(content=cfg["system_prompt"])] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


# ── Build Graph ────────────────────────────────────────────────────────────
def build_graph():
    tool_node = ToolNode(ALL_TOOLS)
    
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")
    
    return graph.compile()


# Singleton
_graph = None

def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
