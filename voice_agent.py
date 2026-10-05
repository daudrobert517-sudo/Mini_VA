import sounddevice as sd
import soundfile as sf
import wave
import requests
import subprocess
import os
import re
import sys
import time

from faster_whisper import WhisperModel


# ==============================
# CONFIGURATION
# ==============================

SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen3:4b"

PIPER_MODEL = "en_US-lessac-medium"

RECORDING_FILE = "recording.wav"
RESPONSE_FILE = "response.wav"

EXIT_PHRASES = {"goodbye", "goodbye assistant", "exit", "quit", "stop"}


# ==============================
# LOAD WHISPER
# ==============================

print("Loading Whisper model...")

whisper_model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Whisper ready.")


# ==============================
# RECORD AUDIO
# ==============================

def record_audio():

    print("\n🎤 Speak now...")

    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16"
    )

    sd.wait()

    with wave.open(RECORDING_FILE, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())

    print("Recording finished.")


# ==============================
# SPEECH TO TEXT
# ==============================

def transcribe_audio():

    print("Transcribing...")

    segments, info = whisper_model.transcribe(
        RECORDING_FILE,
        language="en",
        task="transcribe"
    )

    text = ""

    for segment in segments:
        text += segment.text

    return text.strip()


# ==============================
# ASK OLLAMA
# ==============================

def ask_ollama(user_text, conversation):

    print("\n🤖 Thinking...")

    system_prompt = """
You are a concise local AI voice assistant.
Always respond in English.
Answer the user's request directly in one or two short sentences.
Use plain conversational text only. Do not explain your reasoning.
After thinking silently, begin the answer with FINAL: and put only the answer after it.
Do not use markdown, bullet points, emojis, or complicated formatting.
Do not mention that you are running locally unless asked.
"""

    conversation.append({"role": "user", "content": user_text})

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": conversation,
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1024
                }
            },
            timeout=120
        )
        response.raise_for_status()
    except requests.RequestException as error:
        details = error.response.text if error.response is not None else str(error)
        print(f"Ollama request failed: {details}")
        conversation.pop()
        return "I couldn't reach the language model. Please check that Ollama is running."

    result = response.json()
    answer = result.get("message", {}).get("content", "").strip()
    answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()
    if "FINAL:" in answer:
        answer = answer.rsplit("FINAL:", 1)[1].strip()
    else:
        quoted_answers = re.findall(r'["“](.+?)["”]', answer, flags=re.DOTALL)
        answer = quoted_answers[-1].strip() if quoted_answers else ""

    answer = " ".join(answer.split())
    if not answer:
        answer = "I couldn't produce a concise answer."
    conversation.append({"role": "assistant", "content": answer})
    return answer


# ==============================
# TEXT TO SPEECH
# ==============================

def text_to_speech(text):

    print("\n🔊 Generating voice...")

    command = [
        sys.executable,
        "-m",
        "piper",
        "--model",
        os.path.join(os.path.dirname(__file__), f"{PIPER_MODEL}.onnx"),
        "--output_file",
        RESPONSE_FILE
    ]

    process = subprocess.run(
        command,
        input=text,
        text=True,
        encoding="utf-8",
        capture_output=True
    )

    if process.returncode != 0:
        print("Piper error:")
        print(process.stderr)
        return False

    return True


# ==============================
# PLAY AUDIO
# ==============================

def play_audio():

    print("🔊 Speaking...")

    audio, sample_rate = sf.read(RESPONSE_FILE)

    sd.play(audio, sample_rate)

    sd.wait()


# ==============================
# MAIN
# ==============================

def main():

    print("\n==============================")
    print("      LOCAL AI VOICE AGENT")
    print("==============================")

    conversation = [{
        "role": "system",
        "content": """
You are a concise local AI voice assistant.
Always respond in English.
Answer the user's request directly in one or two short sentences.
Use plain conversational text only. Do not explain your reasoning.
After thinking silently, begin the answer with FINAL: and put only the answer after it.
Do not use markdown, bullet points, emojis, or complicated formatting.
Do not mention that you are running locally unless asked.
"""
    }]

    while True:
        record_audio()

        user_text = transcribe_audio()

        if not user_text:
            print("I couldn't understand you. Please try again.")
            continue

        print(f"\n👤 You: {user_text}")

        if user_text.lower().strip(" .!?'") in EXIT_PHRASES:
            print("Goodbye.")
            break

        ai_response = ask_ollama(user_text, conversation)

        print(f"\n🤖 AI: {ai_response}")

        success = text_to_speech(ai_response)

        if success:
            play_audio()

        print("\nReady for another question.")


if __name__ == "__main__":
    main()