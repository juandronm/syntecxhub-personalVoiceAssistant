import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv(dotenv_path="src/.env")

# Initialize the Hugging Face client with your HF_API_KEY
client = InferenceClient(token=os.getenv("HF_API_KEY"))

try:
    print("Testing API...")
    # Using a known tiny model for ASR to test if the problem is the model or the file
    # First let's check if the file exists
    if not os.path.exists("multilingual_sample.wav"):
        print("ERROR: multilingual_sample.wav does not exist!")
    else:
        result = client.automatic_speech_recognition(
            audio="multilingual_sample.wav", 
            model="ibm-granite/granite-4.0-1b-speech"
        )
        print("Cloud STT Output:", result.text)
except Exception as e:
    import traceback
    print("Exact Error:", repr(e))
    traceback.print_exc()
