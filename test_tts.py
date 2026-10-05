import sounddevice as sd
import soundfile as sf

audio, sample_rate = sf.read("test_voice.wav")

print("Playing voice...")

sd.play(audio, sample_rate)
sd.wait()

print("Finished.")