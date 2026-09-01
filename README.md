# Zerodha Kite MCP Portfolio Agent

An interactive Python portfolio assistant built with Google ADK, OpenAI through LiteLLM, and Zerodha's hosted Kite MCP server.

The agent can retrieve authenticated, live portfolio data and market information. It does not fabricate financial values and requires explicit user confirmation before any order action.

## Prerequisites

- Python 3.14 (the project was validated with Python 3.14.3)
- An OpenAI API key
- A Zerodha Kite account to authorize live portfolio access

## Setup

1. Create and activate a virtual environment:

   ```powershell
   py -3.14 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create `.env` from `.env.example` and set your OpenAI key:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   ```

## Run

```powershell
py -3.14 GPT_MCP.py
```

On the first portfolio request, the agent may call Kite's `login` tool and print an authorization URL. Open it in a browser, finish the Kite login, then return to the same running terminal and reply that login is complete. The same MCP session remains available for later prompts.

Example prompts:

```text
Can you retrieve my holdings?
Check current positions (intraday/derivatives)
What is my available margin?
```

Enter `exit` or `quit` to close the agent cleanly.

## Repository Contents

- `GPT_MCP.py`: working interactive OpenAI and Kite MCP agent.
- `test_3.py`: earlier experiment investigating a persistent MCP connection.
- `test_kite_tools.py`: direct SSE endpoint connectivity experiment.
- `Test.py`, `Test2.py`, `test_content.py`, `test_model.py`, `TestopenAI.py`: exploratory ADK, model, and message-construction scripts.
- `portfolio_agent/agent.py`: earlier local-agent prototype.
- `DETAILS.txt`: implementation notes, trial history, and known non-fatal warnings.

## Notes

- The hosted endpoint is `https://mcp.kite.trade/mcp`; no locally configured Kite API key is required for hosted mode.
- Do not commit `.env`. It contains the OpenAI API key.
- Read-only portfolio and market actions work through the hosted server. The server restricts destructive trade operations.
