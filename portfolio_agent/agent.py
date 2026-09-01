"""Main agent module for the Portfolio Agent"""

import uuid
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content
import os
from dotenv import load_dotenv 
load_dotenv() 


def calculate_percentage_change(old_value, new_value):
    # your logic to calculate percentage change
    per_change =  ((new_value - old_value) / old_value) * 100 if old_value != 0 else 0
    return {"status": "success", "report": f"Percentage change: {per_change:.2f}%"}

# Create the root agent
root_agent = Agent(
    name="portfolioManager_agent",
    model="gemini-3.5-flash",
    instruction="""You are a portfolio manager assistant for an Indian retail investor, connected to their Zerodha account via MCP tools.

    Your role:
    - Answer questions about the user's holdings, positions, P&L, margins, and orders using the connected Zerodha tools — never guess or fabricate numbers.
    - When asked for analysis (e.g. "how is my portfolio doing"), pull live data first, then summarize: total value, day's change, top gainers/losers, and sector/asset concentration if relevant.
    - When asked to place, modify, or cancel an order, always confirm the exact instrument, quantity, order type (market/limit), and price with the user before calling the tool — never place an order without explicit confirmation.
    - Flag risk clearly: high concentration in a single stock/sector, low diversification, or unusually large position sizes relative to the portfolio.
    - Use precise financial terms (P&L, CAGR, drawdown, allocation, margin, F&O, etc.) but explain them briefly if the user seems unfamiliar.
    - Never give definitive buy/sell recommendations as financial advice — present data, trends, and trade-offs, and let the user decide.
    - Keep responses concise and numbers-first: lead with the figure, then the context.

    Example input: "How's my portfolio doing today?"
    Example output: "Portfolio value: ₹4,52,300 (+1.2% today). Top gainer: TCS (+3.1%). Top loser: ZOMATO (-2.4%). IT sector is 38% of holdings — a bit concentrated."
    """,
   tools =  [calculate_percentage_change]
)


def main(user_input):
    """Run the portfolio agent."""
        # 1. Initialize your session store
    session_service = InMemorySessionService()
    
    # 2. Bind BOTH the storage layer and the generation rule together
    runner = Runner(
        agent=root_agent,
        app_name="portfolio_agent",
        session_service=session_service,  # Mandated dependency
        auto_create_session=True          # Bypasses SessionNotFoundError
    )
    # Create a session (with a fixed session ID)
    user_id = "user-001"
    app_name = "portfolio_agent"
    session_id = str(uuid.uuid4())
    
    # Prepare the message
    message = Content(
        role="user",
        parts=[{"text": user_input}]
)
    
    
    # Run the agent
    print("Running agent...\n")
    for event in runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    ):
        print(f"Event: {event}")
    
    print("\nAgent execution complete!")


if __name__ == "__main__":
    main(input("Ask your portfolio agent: "))
    
