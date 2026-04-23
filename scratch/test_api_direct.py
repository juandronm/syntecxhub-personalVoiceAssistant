import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="c:/Users/juanr/OneDrive/Escritorio/SYNTECXHUB/personalVoiceAssistant/src/.env")
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
headers = {
    "Authorization": f"Bearer {os.getenv('HF_API_KEY')}",
    "Content-Type": "audio/m4a"
}

with open(r"c:\Users\juanr\OneDrive\Escritorio\SYNTECXHUB\personalVoiceAssistant\src\audios\firstTry.m4a", "rb") as f:
    data = f.read()

response = requests.post(API_URL, headers=headers, data=data)
print("Status:", response.status_code)
print("Response:", response.text)
