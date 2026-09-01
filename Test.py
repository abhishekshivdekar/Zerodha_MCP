

"""ADK Portfolio Agent connected to Zerodha Kite MCP."""

import asyncio
import uuid

from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import (
    McpToolset,
    StreamableHTTPConnectionParams,
)
from google.genai.types import Content


load_dotenv()


# ---------------------------------------------------------
# 1. Connect to the remote Kite MCP Server
# ---------------------------------------------------------

toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mcp.kite.trade/mcp",
        headers={"User-Agent": "Portfolio-Agent"},
        timeout=10.0,
        sse_read_timeout=300.0,
        terminate_on_close=True,
    )
)


# ---------------------------------------------------------
# 2. Create the ADK Agent
# ---------------------------------------------------------

portfolio_manager_agent = Agent(
    name="portfolioManager_agent",
    model="gemini-3.5-flash",
    instruction="""
    You are a portfolio manager assistant for an Indian retail investor.

    You are connected to the user's Zerodha account through Kite MCP.

    When the user asks about their portfolio, holdings, positions,
    orders, margins, or market data, use the appropriate MCP tool.

    Never fabricate financial data.
    """,
    tools=[toolset],
)


# ---------------------------------------------------------
# 3. Run the ADK Agent
# ---------------------------------------------------------

async def main():

    # ADK session storage
    session_service = InMemorySessionService()

    # ADK Runner
    runner = Runner(
        agent=portfolio_manager_agent,
        app_name="portfolio_agent",
        session_service=session_service,
        auto_create_session=True,
    )

    user_id = "user-001"

    # One ADK session for this interactive conversation
    session_id = str(uuid.uuid4())

    print("Portfolio Agent started.")
    print("Type 'exit' or 'quit' to stop.")

    while True:

        user_input = input("\nAsk: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Convert user input into an ADK message
        message = Content(
            role="user",
            parts=[{"text": user_input}],
        )

        print("\nRunning agent...\n")

        # Execute the agent
        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):

            # Show useful information instead of dumping
            # the entire ADK Event object.
            if event.content and event.content.parts:

                for part in event.content.parts:

                    if part.text:
                        print(f"AGENT: {part.text}")

                    elif part.function_call:
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

        print("\n--- Ready for next question ---")


if __name__ == "__main__":
    asyncio.run(main())