# Personal Voice Assistant

A Python-based personal voice assistant that listens to your voice commands, processes them locally, and responds with spoken audio. It uses Hugging Face's Inference API for powerful Speech-to-Text (STT) and LLM capabilities, paired with local text-to-speech engines.

## ✨ Features

- **🎙️ Speech-to-Text**: Uses OpenAI's `whisper-large-v3-turbo` model (via Hugging Face) to accurately transcribe live audio from your microphone.
- **⚡ Command execution**: Instantly maps specific spoken phrases to actions (e.g., checking the time, searching Google, or opening system apps like Calculator or Notepad).
- **🧠 AI Conversation Fallback**: For general questions, it routes your transcribed speech to the `meta-llama/Llama-3.1-8B-Instruct` model to generate intelligent responses.
- **🔊 High-Quality Speech**: Uses a two-layer Text-to-Speech (TTS) system:
  1. `pyttsx3` for fast, offline, and standard system voices.
  2. `edge-tts` as a high-quality, multilingual fallback that sounds incredibly natural.

## 🛠️ Requirements

- Python 3.10+ (tested on Python 3.13)
- A free Hugging Face account and Access Token
- Microphone and Speakers

## 🚀 Setup & Installation

1. **Clone or download the repository**

2. **Set up a Python virtual environment**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install the dependencies**
   ```bash
   pip install python-dotenv huggingface_hub sounddevice soundfile pyttsx3 edge-tts imageio-ffmpeg
   ```
   *(Note: You may need to install `ffmpeg` system-wide if `imageio-ffmpeg` doesn't cover your OS requirements.)*

4. **Configure your API Key**
   Create a file named `.env` in the `src/` directory and add your Hugging Face API key:
   ```env
   HF_API_KEY=your_hugging_face_token_here
   ```

## 🎮 Usage

To start the voice assistant, simply run:

```bash
python src/main.py
```

The assistant will begin listening to your microphone. **Press `Enter`** when you are finished speaking to process the audio.

### ⌨️ Testing with Text (Dry Run)
If you don't want to use your microphone or want to test specific commands quietly, you can use the command-line flags:

```bash
# Test a rule command without audio
python src/main.py --text-command "What time is it?"

# Test opening an app without actually launching it (Dry Run)
python src/main.py --text-command "Open calculator" --dry-run-actions

# Test the LLM without reading the response out loud
python src/main.py --text-command "Tell me a joke" --no-speech
```

## 🗣️ Supported Commands

The assistant currently recognizes the following natural language triggers:

- **Time**: *"What time is it?"* or *"Tell me the time"*
- **Web Search**: *"Search the web for Python tutorials"* or *"Google how to bake a cake"*
- **Open Apps**: *"Open calculator"*, *"Open notepad"*, *"Open browser"*, *"Open YouTube"*
- **General Questions**: Any other phrase will be sent to the AI (e.g., *"Who was the first person on the moon?"*)

*(Note: The command matcher is flexible and ignores filler words like "the", "a", or punctuation.)*
