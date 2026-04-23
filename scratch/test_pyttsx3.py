import pyttsx3

try:
    engine = pyttsx3.init()
    engine.say("Hello, this is a test.")
    engine.runAndWait()
    print("pyttsx3: SUCCESS")
except Exception as e:
    print(f"pyttsx3: FAILED - {e}")
