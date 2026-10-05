# Mini Voice Agent

A local voice assistant that records speech, transcribes it with Whisper, sends
the transcription to Ollama for a response, and reads the response aloud with
Piper.

## How it works

1. The app records five seconds of audio from your default microphone.
2. [faster-whisper](https://github.com/SYSTRAN/faster-whisper) transcribes the
   recording locally using the `base` model.
3. The transcription is sent to the local Ollama API, using `qwen3:4b` by
   default.
4. [Piper](https://github.com/OHF-Voice/piper1-gpl) generates speech, which is
   played through your default audio output.

The agent keeps conversation context while it is running. Say “goodbye,”
“exit,” “quit,” or “stop” to end the session.

## Project files

- `voice_agent.py` — continuous voice assistant with transcription, Ollama
  chat, and text-to-speech.
- `voice_to_ai.py` — single recording and transcription sent to Ollama's
  generate API; does not use Piper for playback.
- `test_voice.py` — records a short audio sample and transcribes it.
- `test_tts.py` — plays `test_voice.wav`; provide that file locally before
  running this script.
- `AI_Voice_pipeline.png` and `Model_workflow.png` — project diagrams.

## Requirements

- Windows with Python 3.10 or newer.
- A working microphone and audio output device.
- [Ollama](https://ollama.com/) installed and running locally.
- The Python packages listed below.
- Piper voice model files for the full voice agent.

## Setup

Open PowerShell in the project directory and create a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install sounddevice soundfile requests faster-whisper piper-tts
```

If PowerShell prevents activation, either allow script activation for your user
or run the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install sounddevice soundfile requests faster-whisper piper-tts
```

Install and start Ollama, then download the model configured in the scripts:

```powershell
ollama pull qwen3:4b
```

The first run of `faster-whisper` downloads its `base` transcription model.
Internet access may be needed for this initial download.

### Piper voice model

The full agent expects these two files in the project directory:

- `en_US-lessac-medium.onnx`
- `en_US-lessac-medium.onnx.json`

Download the matching US English Lessac medium voice model and its JSON
configuration from the [Piper voices collection](https://huggingface.co/rhasspy/piper-voices).
Keep the filenames above unchanged. The `.onnx` model is large and excluded
from Git, so download it separately after cloning the project.

## Run

Start Ollama, connect a microphone, and run:

```powershell
python voice_agent.py
```

To run the one-shot recording/transcription and Ollama generate example:

```powershell
python voice_to_ai.py
```

To test microphone recording and transcription without Ollama:

```powershell
python test_voice.py
```

To test audio playback, place a local `test_voice.wav` in the project directory
and run:

```powershell
python test_tts.py
```

## Configuration

The main settings are at the top of `voice_agent.py`:

- `SAMPLE_RATE` and `CHANNELS` — microphone recording format.
- `RECORD_SECONDS` — length of each recording.
- `OLLAMA_URL` and `OLLAMA_MODEL` — local Ollama API and model.
- `PIPER_MODEL` — Piper voice model filename prefix.
- `RECORDING_FILE` and `RESPONSE_FILE` — temporary audio file paths.

`voice_to_ai.py` has its own Ollama URL and model settings. If you change the
model there, make sure it is available in Ollama.

## Local files and privacy

Recordings and generated speech are written to `.wav` files in the project
directory. These files are excluded from Git by `.gitignore`. Whisper runs on
your computer; the recognized text is sent to your local Ollama service.
Avoid publishing recordings or other private data.
