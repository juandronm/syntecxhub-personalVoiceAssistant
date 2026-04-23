import torchaudio
import sys

try:
    waveform, sample_rate = torchaudio.load(r"c:\Users\juanr\OneDrive\Escritorio\SYNTECXHUB\personalVoiceAssistant\src\audios\firstTry.m4a")
    print(f"Success! Shape: {waveform.shape}, SR: {sample_rate}")
    torchaudio.save(r"c:\Users\juanr\OneDrive\Escritorio\SYNTECXHUB\personalVoiceAssistant\src\audios\firstTry.wav", waveform, sample_rate)
    print("Saved as wav")
except Exception as e:
    print("Error:", repr(e))
