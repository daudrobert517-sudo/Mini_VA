import sounddevice as sd
import wave
import requests
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
DURATION = 5
CHANNELS = 1

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:4b"


def record_audio():
    print("\n🎤 Speak now...")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16"
    )

    sd.wait()

    with wave.open("recording.wav", "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())

    print("Recording finished.")


def transcribe_audio(model):
    print("Transcribing...")

    segments, info = model.transcribe("recording.wav")

    text = ""

    for segment in segments:
        text += segment.text

    return text.strip()


def ask_ollama(prompt):
    print("\n🤖 Thinking...")

    system_prompt = """
You are a helpful AI voice assistant.
Always respond in English.
Keep your responses natural and conversational.
Do not use Chinese or any other language unless the user specifically asks for it.
Keep answers reasonably short because your responses will be spoken aloud.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "system": system_prompt,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7
            }
        }
    )

    response.raise_for_status()

    return response.json()["response"]


print("Loading Whisper model...")

whisper_model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

record_audio()

user_text = transcribe_audio(whisper_model)

print(f"\nYou: {user_text}")

if user_text:
    ai_response = ask_ollama(user_text)

    print(f"\nAI: {ai_response}")

else:
    print("I could not understand anything. Please try again.")