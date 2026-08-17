import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def llm_review(code: str) -> str:
    prompt = f"""
You are a senior software engineer performing a code review.

Review the following Python code and provide:
- bugs or logical issues
- performance concerns
- readability improvements
- best practice suggestions

Be concise and practical.

Code:
{code}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are a strict code reviewer."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
