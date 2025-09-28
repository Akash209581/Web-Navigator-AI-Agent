import os
from openai import OpenAI

_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=_OPENAI_API_KEY) if _OPENAI_API_KEY else None

def ask_gpt(prompt: str) -> str:
    if client is None:
        # Graceful offline fallback
        return "I'm offline right now, but I can still help with built-in commands."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful personal assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"I ran into an AI error: {e}"