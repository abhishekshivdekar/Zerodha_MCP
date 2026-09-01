# %%
import asyncio
import uuid

from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import (
    McpToolset,
    StreamableHTTPConnectionParams,
)
from google.adk.models.google_llm import _ResourceExhaustedError
from google.genai.types import Content

load_dotenv()

toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mcp.kite.trade/mcp",
        headers={"User-Agent": "Portfolio-Agent"},
        timeout=10.0,
        sse_read_timeout=300.0,
        terminate_on_close=True,
    )
)

portfolio_manager_agent = Agent(
    name="portfolioManager_agent",
    model="gemini-3.5-flash-lite",
    instruction="""
    You are a portfolio manager assistant for an Indian retail investor.
    You are connected to the user's Zerodha account through Kite MCP.

    This connection is READ-ONLY except for GTT (Good Till Triggered) orders.
    Regular buy/sell order placement is not available through this connection.

    When the user asks about their portfolio, holdings, positions,
    margins, or market data, use the appropriate MCP tool.

    If a tool call fails because the user is not authenticated, call the
    `login` tool, share the returned URL with the user, and ask them to
    complete login in their browser before retrying.

    Never fabricate financial data.
    """,
    tools=[toolset],
)

session_service = InMemorySessionService()

runner = Runner(
    agent=portfolio_manager_agent,
    app_name="portfolio_agent",
    session_service=session_service,
    auto_create_session=True,
)

user_id = "user-001"
session_id = str(uuid.uuid4())


async def ask_agent(user_input: str, max_retries: int = 3):
    """Send one message to the agent, printing tool calls and responses.
    Retries automatically on 429 rate-limit errors."""
    message = Content(
        role="user",
        parts=[{"text": user_input}],
    )

    for attempt in range(max_retries):
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(f"AGENT: {part.text}")
                        elif part.function_call:
                            print(f"FUNCTION CALL: {part.function_call.name} {part.function_call.args}")
                        elif part.function_response:
                            print(f"FUNCTION RESPONSE: {part.function_response.name}")
            return
        except _ResourceExhaustedError:
            if attempt < max_retries - 1:
                print(f"\n⏳ Rate limited. Waiting 25s before retry ({attempt + 1}/{max_retries})...")
                await asyncio.sleep(25)
            else:
                print("\n❌ Still rate-limited after retries. Try again later or switch models.")


async def close_toolset():
    """Call this once when you're completely done."""
    if hasattr(toolset, "close"):
        await toolset.close()


print("✅ Portfolio Agent ready.")

# # %%
# await ask_agent("What are my current holdings?")

# # %%
# await ask_agent("What's my available margin?")

# # %%
# await close_toolset()