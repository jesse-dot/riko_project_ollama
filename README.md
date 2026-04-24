# Project Riko

Project Riko is a anime focused LLM project by Just Rayen. She listens, and remembers your conversations. It combines a local Ollama LLM, GPT-SoVITS voice synthesis, and Faster-Whisper ASR into a fully configurable conversational pipeline.

**tested with python 3.10 Windows >10 and Linux Ubuntu**
## ✨ Features

- 💬 **LLM-based dialogue** using a local Ollama server (configurable system prompts)
- 🧠 **Conversation memory** to keep context during interactions
- 🔊 **Voice generation** via GPT-SoVITS API
- 🎧 **Speech recognition** using Faster-Whisper
- 📁 Clean YAML-based config for personality configuration
- 🌐 **WebSocket integration** for real-time frontend communication (VTuber avatar support)


## ⚙️ Configuration

All prompts and parameters are stored in `config.yaml`.

```yaml
OLLAMA_BASE_URL: http://localhost:11434
history_file: chat_history.json
model: "gemma4"
presets:
  default:
    system_prompt: |
      You are a helpful assistant named Riko.
      You speak like a snarky anime girl.
      Always refer to the user as "senpai".

sovits_ping_config:
  text_lang: en
  prompt_lang : en
  ref_audio_path : D:\PyProjects\waifu_project\riko_project\character_files\main_sample.wav
  prompt_text : This is a sample voice for you to just get started with because it sounds kind of cute but just make sure this doesn't have long silences.
  
````

You can define personalities by modiying the config file.
You can change the LLM by setting the `model` value to any Ollama model available on your machine.


## 🛠️ Setup

### GPU Support Selection

Choose the appropriate installation method for your GPU:


#### AMD GPU (ROCm)
```bash
pip install uv
bash install_reqs_amd.sh
```

#### NVIDIA GPU (CUDA)
```bash
pip install uv
bash install_reqs.sh
```

---

## 🟠 AMD/CPU-Only (No NVIDIA) Setup Guide

This section is for users running Riko and GPT-SoVITS on AMD GPUs (without ROCm) or on CPU-only systems (including most laptops/desktops without NVIDIA GPUs). These steps are tested on Linux (Manjaro/Arch), but apply to any OS where you want CPU-only operation.

### 1. Python Environment

- Use **Python 3.10** (recommended for compatibility).
- Create a new virtual environment:
  ```bash
  python3.10 -m venv .venv
  source .venv/bin/activate
  ```

### 2. Install CPU-Only PyTorch, Torchaudio, TorchCodec

**Do NOT install CUDA or ROCm versions!**

```bash
pip install torch==2.1.0+cpu torchaudio==2.1.0+cpu torchcodec --index-url https://download.pytorch.org/whl/cpu
```

### 3. Install Other Requirements

```bash
pip install -r requirements.txt
pip install -r extra-req.txt --no-deps
```

### 4. Install FFmpeg

- On Linux:
  ```bash
  sudo pacman -S ffmpeg   # (Arch/Manjaro)
  sudo apt install ffmpeg # (Debian/Ubuntu)
  ```
- On Windows: Download ffmpeg.exe and ffprobe.exe and place in project root.
- On macOS: `brew install ffmpeg`

### 5. Download NLTK Resources (for English TTS)

If you see errors about missing NLTK data, run:
```python
import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
```

### 6. Place Model Files

- Download the required model files (.ckpt, .pth, encoder) and place them in the correct folders as described in the GPT-SoVITS README.
- **Common folders:**
  - `GPT_SoVITS/pretrained_models/` (for .ckpt, .pth)
  - `GPT_SoVITS/pretrained_models/sv/` (for eres2net encoder)

### 7. Register Models via API

- Start the GPT-SoVITS server: `python api.py`
- Register your model using the `/set_model` endpoint (see below for example curl command).
- **Speaker name must match** what you use in your TTS client/config (see `character_config.yaml`).
- If you restart the server, you must re-register the model.

### 8. Troubleshooting

- If you see errors about CUDA, torch, or missing libraries, make sure you are using only CPU versions of all packages.
- If you see `'NoneType' object has no attribute 'seek'` or model loading errors, check that your model files are not corrupt and are in the correct folders.
- If you get KeyError or empty/corrupt audio, check your speaker name and model registration.
- If you see NLTK errors, run the download commands above.
- If you see FFmpeg errors, ensure it is installed and in your PATH.

---

You can use the provided script for AMD/CPU setup:

```bash
bash install_reqs_amd.sh
```

---

## Example: Registering a Model via API

```bash
curl -X POST "http://localhost:9880/set_model" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "gpt_path": "GPT_SoVITS/pretrained_models/your_gpt_model.ckpt",
    "sovits_path": "GPT_SoVITS/pretrained_models/your_sovits_model.pth",
    "spk_name": "default"
  }'
```

---

## 🧪 Usage

### 1. Launch the GPT-SoVITS API 

> **Note:**
> - You must register your model with the correct speaker name (see above) every time you restart the GPT-SoVITS server.
> - The speaker name in your config (`character_config.yaml`) must match the one used during model registration.
> - If you get empty audio, KeyError, or model not found, check your registration and speaker name.

### 2. Run the main script:

**CLI Mode (No Frontend):**
```bash
python server/main_chat.py
```

**WebSocket Mode (With VTuber Frontend):**
```bash
python server/main_chat_ws.py
```

**Testing WebSocket Server Only:**
```bash
python server/run_server_only.py
```

The flow:

1. Riko listens to your voice via microphone (push to talk)
2. Transcribes it with Faster-Whisper
3. Passes it to Ollama (with history)
4. Generates a response
5. Synthesizes Riko's voice using GPT-SoVITS
6. Plays the output back to you
7. (WebSocket mode) Broadcasts state to connected frontends for avatar animation

For detailed WebSocket setup and integration, see [README_WEBSOCKET.md](README_WEBSOCKET.md).


## 📌 TODO / Future Improvements

* [x] WebSocket server for frontend integration
* [ ] GUI or web interface
* [ ] Live microphone input support
* [ ] Emotion or tone control in speech synthesis
* [x] VRM model frontend (via WebSocket integration)


## 🧑‍🎤 Credits

* Voice synthesis powered by [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
* ASR via [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
* Language model via [Ollama](https://ollama.com)


## 📜 License

MIT — feel free to clone, modify, and build your own waifu voice companion.
