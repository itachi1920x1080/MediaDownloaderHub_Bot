from openai import AsyncOpenAI
from app.config import settings

# Initialize the async OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def get_chat_response(messages: list[dict]) -> str:
    """
    Sends a list of messages to the OpenAI API and returns the response content.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini", # You can change this to gpt-4 or another model
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        # In a real app, you might want to log this error
        print(f"Error communicating with OpenAI: {e}")
        return "I'm sorry, I'm having trouble connecting to my brain right now."
