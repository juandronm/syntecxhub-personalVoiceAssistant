import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


DEFAULT_STT_MODEL = "openai/whisper-large-v3-turbo"
DEFAULT_CHAT_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
DEFAULT_SYSTEM_PROMPT = "You are a helpful personal voice assistant."
DEFAULT_RECORDING_PATH = Path(__file__).resolve().parent / "audios" / "live_input.wav"


def load_api_key() -> str:
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        raise RuntimeError("HF_API_KEY is missing. Add it to src/.env or your shell environment.")
    return api_key


def record_audio(output_path: Path, duration: float, sample_rate: int, channels: int, device: int | str | None) -> Path:
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "Live recording requires sounddevice and soundfile. "
            "Install them with: .\\.venv\\Scripts\\python.exe -m pip install sounddevice soundfile"
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
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
        max_tokens=512,
    )
    return response.choices[0].message.content


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
        "--duration",
        type=float,
        default=8.0,
        help="Seconds to record when no audio path is provided. Default: 8",
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list_devices:
        list_audio_devices()
        return

    api_key = load_api_key()

    audio_path = args.audio_path or record_audio(
        args.recorded_output,
        duration=args.duration,
        sample_rate=args.sample_rate,
        channels=args.channels,
        device=args.device,
    )

    transcript = transcribe_audio(audio_path, api_key, args.stt_model)
    print("Transcript:")
    print(transcript)

    if args.transcript_only:
        return

    answer = ask_llm(transcript, api_key, args.chat_model, args.system_prompt)
    print("\nLLM response:")
    print(answer)


if __name__ == "__main__":
    main()
