"""ADK Portfolio Agent connected to Zerodha Kite MCP."""

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
# 1. Connect to Zerodha Kite MCP
# ---------------------------------------------------------

kite_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mcp.kite.trade/mcp",
        headers={"User-Agent": "Portfolio-Agent"},
        timeout=10.0,
        sse_read_timeout=300.0,
        terminate_on_close=True,
    )
)


# ---------------------------------------------------------
# 2. Portfolio Manager Agent
# ---------------------------------------------------------

portfolio_manager_agent = Agent(
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
# 3. Run the Agent
# ---------------------------------------------------------

async def main():

    session_service = InMemorySessionService()

    runner = Runner(
        agent=portfolio_manager_agent,
        app_name="portfolio_agent",
        session_service=session_service,
        auto_create_session=True,
    )

    user_id = "user-001"
    session_id = str(uuid.uuid4())

    print("Portfolio Agent started.")
    print("Model: OpenAI GPT-5 Mini")
    print("Type 'exit' or 'quit' to stop.")

    try:
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

            async for event in runner.run_async(
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
    finally:
        await kite_mcp.close()
        await runner.close()


if __name__ == "__main__":
    asyncio.run(main())