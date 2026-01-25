import requests
import os

DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")

def chat_with_user(messages):
    headers = {
        "Authorization": f"Bearer {DOUBAO_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "doubao-pro-32k",
        "messages": messages,
        "temperature": 0.7
    }

    resp = requests.post(DOUBAO_API_URL, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
