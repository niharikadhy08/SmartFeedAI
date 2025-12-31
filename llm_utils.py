import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You talk directly to the user using only 'you' and 'your'. Never use 'I', 'I'm', 'we', or 'my'. Be friendly and simple."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content


def explain_recommendation(post_text, post_tags, user_interests):
    prompt = f"""
Your interests are: {user_interests}

This post says:
"{post_text}"

Tags: {post_tags}

Explain in very simple words why YOU are seeing this post in YOUR feed.
Talk directly to the user.
Do NOT use first person words like I, I'm, we, or my.
"""
    return call_llm(prompt)

