"""ADK Portfolio Agent connected to Zerodha Kite MCP.

Fix vs original: the McpToolset connection is opened ONCE and held open
for the entire interactive session (a single `async with` scope around
the whole input loop), instead of letting each `runner.run()` call
implicitly reconnect. That reconnect-per-turn was creating a brand new
Kite MCP session on every question, which discarded the login you'd
just completed.
"""

import asyncio
import uuid

from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import (
    McpToolset,
    StreamableHTTPConnectionParams,
)
from google.genai.types import Content


load_dotenv()


# ---------------------------------------------------------
# 1. Portfolio Manager Agent (kite_mcp passed in later)
# ---------------------------------------------------------

def build_agent(kite_mcp: McpToolset) -> Agent:
    return Agent(
        name="portfolioManager_agent",

        model=LiteLlm(
            model="openai/gpt-5-mini"
        ),

        instruction="""
        You are a portfolio manager assistant for an Indian retail investor.

        You are connected to the user's Zerodha account through Kite MCP.

        Your responsibilities:

        1. Holdings
           - Use the appropriate MCP tool to retrieve live holdings.
           - Never invent holdings, quantities, prices, or P&L.

        2. Portfolio analysis
           - When asked how the portfolio is performing, retrieve
             relevant live data first.
           - Summarize portfolio value, P&L, gainers, losers and
             concentration when the available data supports it.

        3. Market information
           - Use Kite MCP market-data tools for current prices
             and market information.

        4. Risk
           - Highlight concentration, unusually large positions,
             and diversification concerns when supported by data.

        5. Orders
           - Never place, modify, or cancel an order without
             explicit confirmation from the user.
           - Before an order action, confirm the instrument,
             transaction type, quantity, order type, and price
             where applicable.

        6. Financial advice
           - Do not provide definitive buy/sell recommendations.
           - Present data, risks, and trade-offs.

        Always use live MCP data when the question requires it.
        Never fabricate financial numbers.
        """,

        tools=[kite_mcp],
    )


# ---------------------------------------------------------
# 2. Run the Agent — single persistent MCP connection
# ---------------------------------------------------------

async def main():

    session_service = InMemorySessionService()

    user_id = "user-001"
    session_id = str(uuid.uuid4())

    # KEY CHANGE: kite_mcp is created and entered ONCE here, and the
    # `async with` block wraps the ENTIRE interactive loop below. The
    # connection (and whatever Kite session id it negotiates) now lives
    # for the whole program run instead of being rebuilt every turn.
    kite_mcp = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://mcp.kite.trade/mcp",
            headers={"User-Agent": "Portfolio-Agent"},
            timeout=10.0,
            sse_read_timeout=300.0,
            terminate_on_close=True,
        )
    )

    async with kite_mcp:
        agent = build_agent(kite_mcp)

        runner = Runner(
            agent=agent,
            app_name="portfolio_agent",
            session_service=session_service,
            auto_create_session=True,
        )

        print("Portfolio Agent started.")
        print("Model: OpenAI GPT-5 Mini")
        print("Type 'exit' or 'quit' to stop.")

        while True:

            user_input = input("\nAsk: ")

            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            message = Content(
                role="user",
                parts=[{"text": user_input}],
            )

            print("\nRunning agent...\n")

            for event in runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=message,
            ):

                if event.content and event.content.parts:

                    for part in event.content.parts:

                        if part.function_call:
                            print(
                                f"FUNCTION CALL: "
                                f"{part.function_call.name} "
                                f"{part.function_call.args}"
                            )

                        elif part.function_response:
                            print(
                                f"FUNCTION RESPONSE: "
                                f"{part.function_response.name}"
                            )

                        elif part.text:
                            print(f"AGENT: {part.text}")

            print("\n--- Ready for next question ---")

    # kite_mcp connection closes cleanly here, once, after the loop exits
    # — instead of being torn down and reopened after every single turn.


if __name__ == "__main__":
    asyncio.run(main())