import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path="c:/Users/juanr/OneDrive/Escritorio/SYNTECXHUB/personalVoiceAssistant/src/.env")

client = OpenAI(
    base_url="https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct/v1/",
    api_key=os.getenv("HF_API_KEY")
)

try:
    print("Testing chat completion...")
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct",
        messages=[{"role": "user", "content": "Say hello!"}],
        max_tokens=10
    )
    print("Chat Success:", response.choices[0].message.content)
except Exception as e:
    print("Chat Error:", e)
