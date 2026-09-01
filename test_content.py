from google.genai.types import Content

# Try to create a content object
content = Content(role="user", parts=[{"text": "Hello"}])
print(f"Content object: {content}")
print(f"Role: {content.role}")
