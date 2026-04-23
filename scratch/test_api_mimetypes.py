import mimetypes
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Force Python's mimetypes to return 'audio/m4a' for .m4a files
mimetypes.add_type('audio/m4a', '.m4a')
mimetypes.add_type('audio/m4a', '.mp4')

load_dotenv(dotenv_path="c:/Users/juanr/OneDrive/Escritorio/SYNTECXHUB/personalVoiceAssistant/src/.env")

client = InferenceClient(token=os.getenv("HF_API_KEY"))

try:
    print("Mime type for .m4a:", mimetypes.guess_type("test.m4a"))
    print("Sending audio to the cloud...")
    result = client.automatic_speech_recognition(
        audio=r"c:\Users\juanr\OneDrive\Escritorio\SYNTECXHUB\personalVoiceAssistant\src\audios\firstTry.m4a",
        model="openai/whisper-large-v3-turbo"
    )
    print("\nCloud STT Output:", result.text)
except Exception as e:
    print("Exact Error:", repr(e))
