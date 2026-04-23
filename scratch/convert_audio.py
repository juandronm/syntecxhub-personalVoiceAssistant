import os
import subprocess
import imageio_ffmpeg

input_file = r"c:\Users\juanr\OneDrive\Escritorio\SYNTECXHUB\personalVoiceAssistant\src\audios\firstTry.m4a"
output_file = r"c:\Users\juanr\OneDrive\Escritorio\SYNTECXHUB\personalVoiceAssistant\src\audios\firstTry.wav"

try:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print("Converting using ffmpeg...")
    subprocess.run([ffmpeg_exe, "-y", "-i", input_file, output_file], check=True)
    print(f"Successfully converted to {output_file}")
except Exception as e:
    print("Error during conversion:", repr(e))
