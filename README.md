# 🧠 Smart Research Agent

> AI-powered agentic system with web search, PDF reading, memory & tool orchestration — built with LangGraph + FastAPI + Python

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green?style=flat-square&logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-1.2-orange?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-1.3-yellow?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-ready-blue?style=flat-square&logo=docker)
![Open Source](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🎯 What It Does

A production-grade **single AI agent** that autonomously uses tools to:
- 🔍 **Search the web** for real-time information (via SearXNG - open source)
- 📄 **Read & analyze PDFs** uploaded by the user
- 📋 **Summarize** long documents into key points
- 🧮 **Perform calculations** safely and accurately
- 🧠 **Remember context** across the full conversation (session memory)
- 🎤 **Voice input** - Speak your questions (STT)
- 🔊 **Voice output** - AI speaks responses (TTS)
- 🌐 **Serve a clean HTML frontend** — no React, no build step
- ⚡ **Config-driven** — all settings in JSON, zero hardcoded values

---

## 🏗️ Architecture

```
User (HTML Frontend)
       ↓  HTTP
FastAPI Backend  (/api/chat)
       ↓
  Session Memory (in-memory)
       ↓
  LangGraph Agent (Single Agent)
  ┌────────────────────────────┐
  │  Agent Loop (Agentic)      │
  │                            │
  │  1. Agent Node (LLM)       │
  │       ↓                    │
  │  2. Should use tool?       │
  │       ↓                    │
  │  3. Tool Node (execute)    │
  │       ↓                    │
  │  4. Back to Agent (loop)   │
  │       ↓                    │
  │  5. Done? → Return answer  │
  └────────────────────────────┘
       ↓ tools (agent decides)
  ┌──────────┬──────────┬──────────┬────────────┐
  │Web Search│PDF Reader│Summarize │ Calculator │
  │(SearXNG) │  (pypdf) │  (text)  │ (ast.eval) │
  └──────────┴──────────┴──────────┴────────────┘
       ↓
  LLM (Ollama/OpenAI/Anthropic)
```

**Key:** Single agent with 4 tools, not 4 separate agents.

---

## 🎮 Features

### 🤖 Agentic AI
- Single agent with autonomous tool selection
- LangGraph orchestration with agent loop
- Multi-tool chaining in single query
- Session-based conversation memory

### 🛠️ Tools
- **Web Search** - Real-time internet search via SearXNG
- **PDF Reader** - Extract and analyze PDF documents
- **Summarizer** - Condense long text into key points
- **Calculator** - Safe mathematical expressions

### 🎤 Voice Interface
- **Speech-to-Text** - Speak your questions (click 🎤 button)
- **Text-to-Speech** - AI speaks responses automatically
- Browser-based Web Speech API (no backend needed)
- Works in Chrome/Edge

### ⚙️ Configuration
- Switch LLM providers (Ollama/OpenAI/Anthropic)
- Customize system prompts
- Adjust tool parameters
- All via `llm_config.json`

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/smart-research-agent.git
cd smart-research-agent
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp .env.example .env
# Edit .env with your keys
```

### 3. Run
```bash
uvicorn app.main:app --reload
```

Open `http://localhost:8000` — the HTML frontend loads automatically.

### Or with Docker
```bash
docker-compose up
```

---

## 🔑 Setup Requirements

| Component | Required | How to Get |
|-----------|----------|------------|
| **Ollama** | ✅ Yes | [ollama.com](https://ollama.com) |
| **SearXNG** | ✅ Yes | `docker run -d -p 8888:8080 searxng/searxng:latest` |
| **OpenAI API** | ❌ Optional | For GPT-4o instead of Ollama |
| **Anthropic API** | ❌ Optional | For Claude instead of Ollama |

**Default setup uses:**
- Ollama (local, free) for LLM
- SearXNG (open-source, free) for web search
- No API keys needed!

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send message to agent |
| `GET` | `/api/sessions` | List all active sessions |
| `GET` | `/api/history/{session_id}` | Get conversation history |
| `DELETE` | `/api/session/{session_id}` | Clear a session |
| `POST` | `/api/upload-pdf` | Upload PDF for agent to read |
| `GET` | `/health` | Health check |

### Example Request
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Search for latest AI trends 2026", "session_id": "my-session"}'
```

### Example Response
```json
{
  "response": "Here are the latest AI trends...",
  "session_id": "my-session",
  "tools_used": ["web_search"],
  "timestamp": "2026-05-30T10:00:00"
}
```

---

## 🗂️ Project Structure

```
smart-research-agent/
├── app/
│   ├── agent/
│   │   ├── graph.py      # LangGraph agent (nodes, edges, tools binding)
│   │   ├── tools.py      # web_search, read_pdf, summarize, calculate
│   │   └── memory.py     # Session-based conversation memory
│   ├── api/
│   │   ├── routes.py     # FastAPI endpoints
│   │   └── schemas.py    # Pydantic request/response models
│   ├── core/
│   │   └── config.py     # Settings from .env
│   └── main.py           # App entry point + static serving
├── frontend/
│   └── index.html        # Single-file HTML/CSS/JS frontend
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Agent Framework** | LangGraph 1.2 |
| **LLM** | Ollama (qwen3/llama3) - Local |
| **Backend** | FastAPI 0.136 + Uvicorn |
| **Memory** | In-memory dict |
| **Web Search** | SearXNG (open-source) |
| **PDF Processing** | pypdf + LangChain |
| **Voice (STT)** | Web Speech API (browser) |
| **Voice (TTS)** | Speech Synthesis API (browser) |
| **Vector DB** | ChromaDB (optional) |
| **Frontend** | Vanilla HTML + CSS + JS |
| **Config** | JSON (llm_config.json) |
| **Deploy** | Docker + docker-compose |

---

## 🔮 Future Improvements

- [ ] Streaming responses (SSE)
- [ ] Redis for persistent sessions
- [ ] ChromaDB for RAG/vector memory
- [ ] Multi-agent collaboration
- [ ] Auth with JWT
- [ ] React frontend
- [ ] DuckDuckGo search integration
- [ ] OCR for scanned PDFs
- [ ] Multi-language voice support
- [ ] Voice activity detection
- [ ] Custom voice selection

---

## 👤 Author

Built by a Python Backend Developer specializing in **AI/ML & Generative AI**.

---

## 📄 License

MIT
