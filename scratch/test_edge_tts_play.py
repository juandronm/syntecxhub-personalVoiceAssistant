import asyncio
import os
import subprocess
import edge_tts
import imageio_ffmpeg

async def test_edge_tts():
    output_path = r"c:\Users\juanr\OneDrive\Escritorio\SYNTECXHUB\personalVoiceAssistant\scratch\edge_test.mp3"
    communicate = edge_tts.Communicate("Hello, this is edge TTS test.", "en-US-AndrewMultilingualNeural")
    await communicate.save(output_path)
    print(f"edge-tts: Audio saved ({os.path.getsize(output_path)} bytes)")
    
    # Test playback using ffplay from imageio-ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    ffplay_path = ffmpeg_path.replace("ffmpeg.exe", "ffplay.exe")
    if os.path.exists(ffplay_path):
        print("ffplay found, can play audio")
    else:
        print("ffplay not found, will need alternative playback")
    print("edge-tts: SUCCESS")

asyncio.run(test_edge_tts())
