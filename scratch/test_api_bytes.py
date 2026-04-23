import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv(dotenv_path="c:/Users/juanr/OneDrive/Escritorio/SYNTECXHUB/personalVoiceAssistant/src/.env")

client = InferenceClient(token=os.getenv("HF_API_KEY"))

with open(r"c:\Users\juanr\OneDrive\Escritorio\SYNTECXHUB\personalVoiceAssistant\src\audios\firstTry.m4a", "rb") as f:
    data = f.read()

try:
    print("Sending as bytes with custom headers...")
    response = client.post(
        model="openai/whisper-large-v3-turbo",
        data=data,
        task="automatic-speech-recognition",
        headers={"Content-Type": "audio/m4a"}
    )
    print("Result:", response)
except Exception as e:
    print("Error:", repr(e))
