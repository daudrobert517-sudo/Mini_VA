import sounddevice as sd
import wave
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
DURATION = 5
CHANNELS = 1

print("Recording...")
print("Speak now!")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="int16"
)

sd.wait()

print("Recording finished.")

with wave.open("recording.wav", "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio.tobytes())

print("Loading Whisper...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Transcribing...")

segments, info = model.transcribe("recording.wav")

print("\nYou said:")

for segment in segments:
    print(segment.text)