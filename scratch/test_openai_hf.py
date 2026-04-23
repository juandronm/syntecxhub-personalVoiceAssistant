import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path="c:/Users/juanr/OneDrive/Escritorio/SYNTECXHUB/personalVoiceAssistant/src/.env")

client = OpenAI(
    base_url="https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo/v1/",
    api_key=os.getenv("HF_API_KEY")
)

try:
    print("\nTesting audio transcription...")
    with open(r"c:\Users\juanr\OneDrive\Escritorio\SYNTECXHUB\personalVoiceAssistant\src\audios\firstTry.wav", "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="openai/whisper-large-v3-turbo",
            file=f
        )
    print("Audio Success:", transcription.text)
except Exception as e:
    print("Audio Error:", e)
