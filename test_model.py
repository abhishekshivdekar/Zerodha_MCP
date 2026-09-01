from google.adk import Agent

# Try to see what the agent expects
try:
    agent = Agent(
        name="test",
        model="gemini-3.5-flash",
        instruction="test"
    )
    print("String model works!")
    print(f"Agent: {agent}")
except Exception as e:
    print(f"String model error: {type(e).__name__}: {e}")
