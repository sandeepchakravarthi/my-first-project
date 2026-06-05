import os
import json
import uuid
import httpx
import ast
from typing import Optional
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "llm_config.json")


def _load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)


def _tool_cfg(name: str) -> dict:
    return _load_config()["tools"][name]


def _error_msg(key: str, **kwargs) -> str:
    return _load_config()["error_messages"][key].format(**kwargs)


@tool
def web_search(query: str) -> str:
    """Search the web using SearXNG meta-search engine."""
    cfg = _tool_cfg("web_search")
    
    try:
        import requests
        response = requests.get(
            f"{cfg['base_url']}/search",
            params={
                "q": query,
                "format": "json",
                "engines": ",".join(cfg.get("engines", [])),
                "categories": ",".join(cfg.get("categories", ["general"]))
            },
            timeout=cfg["timeout"]
        )
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return f"No results found for: '{query}'"
        
        output = f"Web search results for: '{query}'\n\n"
        for i, r in enumerate(results[:cfg["max_results"]], 1):
            output += f"{i}. {r.get('title', '')}\n   {r.get('content', '')[:200]}...\n   URL: {r.get('url', '')}\n\n"
        return output
    except Exception as e:
        return _error_msg("search_error", error=str(e))


@tool
def read_pdf(file_path: str) -> str:
    """Read and extract text content from a PDF file."""
    try:
        if not os.path.exists(file_path):
            return _error_msg("file_not_found", path=file_path)
        
        cfg = _tool_cfg("read_pdf")
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=cfg["chunk_size"],
            chunk_overlap=cfg["chunk_overlap"]
        )
        chunks = splitter.split_documents(pages)
        
        content = f"PDF Content from: {file_path}\n"
        content += f"Total pages: {len(pages)}\n\n"
        for i, chunk in enumerate(chunks[:cfg["max_chunks"]]):
            content += f"--- Section {i+1} ---\n{chunk.page_content}\n\n"
        
        return content
    except Exception as e:
        return _error_msg("pdf_read_error", error=str(e))


@tool
def summarize_text(text: str) -> str:
    """Summarize a long block of text into key bullet points."""
    cfg = _tool_cfg("summarize_text")
    sentences = text.split('. ')
    key_points = sentences[:cfg["max_sentences"]]
    summary = cfg["prefix"]
    for i, point in enumerate(key_points, 1):
        if point.strip():
            summary += f"  {i}. {point.strip()}\n"
    return summary


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        cfg = _tool_cfg("calculate")
        allowed = set(cfg["allowed_chars"])
        if not all(c in allowed for c in expression):
            return cfg["error_message"]
        result = ast.literal_eval(expression)
        return f"Result: {expression} = {result}"
    except Exception as e:
        return _error_msg("calculation_error", error=str(e))


ALL_TOOLS = [web_search, read_pdf, summarize_text, calculate]
TOOL_NAMES = [t.name for t in ALL_TOOLS]
