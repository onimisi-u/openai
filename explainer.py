import os
from dotenv import load_dotenv
from functools import partial

from openai import OpenAI
# Load the .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def send_question(question: str) -> dict:
    return client.chat.completions.create(model="gpt-3.5-turbo-1106",
    temperature=0,
    messages=[
        {"role": "system", "content": "You are a product manager conducting user interviews."},
        {"role": "user", "content": question},
    ])

def retrieve_ai_answer(response: dict) -> str:
    return response.choices[0].message.content


def get_info(question: str, text_input: str) -> str:
    resp = send_question(f"{question}\n\n{text_input}")
    return retrieve_ai_answer(resp)
