from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_tests(code: str):
    """
    Generates functional test cases for the given code snippet.
    """

    prompt = f"""
You are an expert QA engineer and Python tester.

Your task:
Given the following code, generate EXACTLY 10 UNIQUE test cases:
- 5 normal cases
- 3 edge cases
- 2 error cases (invalid input, type mismatch, boundary violations)

STRICT RULES:
- No two test cases may have the same input.
- Each test case must test a different scenario.
- Clearly label the Type: Normal / Edge / Error.
- Provide the expected output for each case.
- Include a short reason explaining what the test covers.
- DO NOT repeat or merge test cases.

Return your answer in this format ONLY:

TEST CASES:
1. Input: ...
   Expected Output: ...
   Type: ...
   Reason: ...

2. Input: ...
   Expected Output: ...
   Type: ...
   Reason: ...

CODE UNDER TEST:
<code>
{code}
</code>
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a professional QA engineer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content
