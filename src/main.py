import argparse
import os
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread
from urllib.parse import quote_plus

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


DEFAULT_STT_MODEL = "openai/whisper-large-v3-turbo"
DEFAULT_CHAT_MODEL = "meta-llama/Llama-3.1-8B-Instruct:cerebras"
DEFAULT_SYSTEM_PROMPT = "You are a helpful personal voice assistant."
DEFAULT_RECORDING_PATH = Path(__file__).resolve().parent / "audios" / "live_input.wav"
SAMPLE_COMMANDS = [
    "What time is it?",
    "Search web for Python tutorials",
    "Open notepad",
    "Open calculator",
    "Open browser",
    "Tell me a joke",
]
APP_COMMANDS = {
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "notepad": "notepad.exe",
    "paint": "mspaint.exe",
    "browser": "https://www.google.com",
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
}


def load_api_key() -> str:
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        raise RuntimeError("HF_API_KEY is missing. Add it to src/.env or your shell environment.")
    return api_key


def record_audio(output_path: Path, duration: float | None, sample_rate: int, channels: int, device: int | str | None) -> Path:
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "Live recording requires sounddevice and soundfile. "
            "Install them with: .\\.venv\\Scripts\\python.exe -m pip install sounddevice soundfile"
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if duration is not None:
        print(f"Recording {duration:g}s from the microphone...")
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype="float32",
            device=device,
        )
        sd.wait()
        sf.write(output_path, audio, sample_rate)
        print(f"Saved recording: {output_path}")
        return output_path

    audio_queue: Queue = Queue()
    stop_recording = Event()

    def audio_callback(indata, frames, time, status) -> None:
        if status:
            print(status)
        audio_queue.put(indata.copy())

    def wait_for_stop_key() -> None:
        input()
        stop_recording.set()

    print("Recording from the microphone. Press Enter to stop...")
    with sf.SoundFile(output_path, mode="w", samplerate=sample_rate, channels=channels) as audio_file:
        with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            dtype="float32",
            device=device,
            callback=audio_callback,
        ):
            Thread(target=wait_for_stop_key, daemon=True).start()
            while not stop_recording.is_set() or not audio_queue.empty():
                try:
                    audio_file.write(audio_queue.get(timeout=0.1))
                except Empty:
                    pass

    print(f"Saved recording: {output_path}")
    return output_path


def list_audio_devices() -> None:
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise RuntimeError(
            "Listing recording devices requires sounddevice. "
            "Install it with: .\\.venv\\Scripts\\python.exe -m pip install sounddevice"
        ) from exc

    print(sd.query_devices())


def transcribe_audio(audio_path: Path, api_key: str, model: str) -> str:
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    provider = os.getenv("HF_STT_PROVIDER", "auto")
    client = InferenceClient(provider=provider, api_key=api_key, timeout=120)
    result = client.automatic_speech_recognition(str(audio_path), model=model)
    text = getattr(result, "text", None)
    if not text and isinstance(result, dict):
        text = result.get("text")
    if not text:
        raise RuntimeError(f"Transcription returned no text: {result}")
    return text


def ask_llm(transcript: str, api_key: str, model: str, system_prompt: str) -> str:
    provider = os.getenv("HF_CHAT_PROVIDER", "auto")
    client = InferenceClient(provider=provider, api_key=api_key, timeout=120)
    response = client.chat_completion(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript},
        ],
        max_tokens=1024,
    )
    return response.choices[0].message.content


def print_sample_commands() -> None:
    print("Sample commands:")
    for command in SAMPLE_COMMANDS:
        print(f"  - {command}")
    print()


def speak(text: str, enabled: bool = True) -> None:
    print(f"Assistant: {text}")
    if not enabled:
        return

    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:
        print(f"TTS unavailable: {exc}")


def normalize_command(command: str) -> str:
    return " ".join(command.lower().strip().split())


def extract_search_query(command: str) -> str | None:
    
    search_phrases = [
        "search web for ",
        "search the web for ",
        "google ",
        "look up ",
        "search for ",
    ]
    for phrase in search_phrases:
        if phrase in command:
            query = command.split(phrase, 1)[1].strip()
            return query or None
    return None


def _clean_command(text: str) -> str:
    """Remove punctuation and collapse whitespace for matching."""
    import re

    return re.sub(r"[^\w\s]", "", text).strip()


def handle_rule_command(command: str, dry_run: bool = False) -> str | None:
    normalized = normalize_command(command)
    if not normalized:
        return "I did not hear a command. Please try again."

    cleaned = _clean_command(normalized)

    # --- Tell time ---
    if "time" in cleaned:
        current_time = datetime.now().strftime("%I:%M %p").lstrip("0")
        return f"The time is {current_time}."

    # --- Web search ---
    search_query = extract_search_query(cleaned)
    if search_query:
        if not dry_run:
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(search_query)}")
        return f"Searching the web for {search_query}."

    # --- Open app / website ---
    # Look for "open" anywhere in the sentence, not just at the start
    if "open" in cleaned:
        # Grab everything after the word "open"
        after_open = cleaned.split("open", 1)[1].strip()
        # Strip common filler words (the, a, my, an)
        for filler in ("the ", "a ", "my ", "an "):
            if after_open.startswith(filler):
                after_open = after_open[len(filler):]
        after_open = after_open.strip()

        # First try exact match, then scan for any known app name
        app_name = None
        if after_open in APP_COMMANDS:
            app_name = after_open
        else:
            for key in APP_COMMANDS:
                if key in after_open:
                    app_name = key
                    break


        if app_name:
            app_target = APP_COMMANDS[app_name]
            if not dry_run:
                if app_target.startswith("http"):
                    webbrowser.open(app_target)
                else:
                    subprocess.Popen([app_target])
            return f"Opening {app_name}."

    # --- Help ---
    if "help" in cleaned or "sample commands" in cleaned:
        return "You can ask me to tell the time, search the web, open notepad, open calculator, or ask a general question."

    return None


def build_response(transcript: str, api_key: str, chat_model: str, system_prompt: str, dry_run_actions: bool = False) -> str:
    rule_response = handle_rule_command(transcript, dry_run=dry_run_actions)
    if rule_response:
        return rule_response
    return ask_llm(transcript, api_key, chat_model, system_prompt)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record live audio, transcribe it, and send the transcript to a chat LLM."
    )
    parser.add_argument(
        "audio_path",
        nargs="?",
        type=Path,
        help="Optional existing audio file. If omitted, audio is recorded from the microphone.",
    )
    parser.add_argument(
        "--text-command",
        help="Handle a typed command instead of recording/transcribing audio.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        help="Optional seconds to record. If omitted, recording continues until you press Enter.",
    )
    parser.add_argument(
        "--recorded-output",
        type=Path,
        default=DEFAULT_RECORDING_PATH,
        help=f"Where to save the live microphone recording. Default: {DEFAULT_RECORDING_PATH}",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Microphone recording sample rate. Default: 16000",
    )
    parser.add_argument(
        "--channels",
        type=int,
        default=1,
        help="Microphone recording channel count. Default: 1",
    )
    parser.add_argument(
        "--device",
        help="Optional sounddevice input device id or name.",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="Print available audio devices and exit.",
    )
    parser.add_argument(
        "--record-only",
        action="store_true",
        help="Record live microphone audio and exit without transcription.",
    )
    parser.add_argument(
        "--stt-model",
        default=os.getenv("HF_STT_MODEL", DEFAULT_STT_MODEL),
        help=f"Speech-to-text model. Default: {DEFAULT_STT_MODEL}",
    )
    parser.add_argument(
        "--chat-model",
        default=os.getenv("HF_CHAT_MODEL", DEFAULT_CHAT_MODEL),
        help=f"Chat model. Default: {DEFAULT_CHAT_MODEL}",
    )
    parser.add_argument(
        "--system-prompt",
        default=os.getenv("ASSISTANT_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT),
        help="System prompt sent with the transcript.",
    )
    parser.add_argument(
        "--transcript-only",
        action="store_true",
        help="Only print the audio transcript without calling the chat LLM.",
    )
    parser.add_argument(
        "--no-speech",
        action="store_true",
        help="Print responses without reading them aloud.",
    )
    parser.add_argument(
        "--dry-run-actions",
        action="store_true",
        help="Show action responses without opening apps or browser tabs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list_devices:
        list_audio_devices()
        return

    print_sample_commands()

    if args.text_command:
        rule_response = handle_rule_command(args.text_command, dry_run=args.dry_run_actions)
        if rule_response:
            speak(rule_response, enabled=not args.no_speech)
            return

        api_key = load_api_key()
        answer = ask_llm(args.text_command, api_key, args.chat_model, args.system_prompt)
        speak(answer, enabled=not args.no_speech)
        return

    audio_path = args.audio_path or record_audio(
        args.recorded_output,
        duration=args.duration,
        sample_rate=args.sample_rate,
        channels=args.channels,
        device=args.device,
    )

    if args.record_only:
        return

    api_key = load_api_key()

    transcript = transcribe_audio(audio_path, api_key, args.stt_model)
    print("Transcript:")
    print(transcript)

    if args.transcript_only:
        return

    answer = build_response(
        transcript,
        api_key,
        args.chat_model,
        args.system_prompt,
        dry_run_actions=args.dry_run_actions,
    )
    speak(answer, enabled=not args.no_speech)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
    except FileNotFoundError as exc:
        print(f"File error: {exc}")
    except RuntimeError as exc:
        print(f"Setup error: {exc}")
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        print("Please check your microphone, internet connection, API key, and installed dependencies.")
