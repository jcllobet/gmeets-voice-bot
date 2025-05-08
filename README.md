# GMeets Joiner

<div align="center">
  <img src="https://img.shields.io/badge/Google%20Meet-00897B?style=for-the-badge&logo=google-meet&logoColor=white" alt="Google Meet"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
</div>

<div align="center">
  <h3>🤖 AI-Powered Google Meet Assistant</h3>
  <p>Automate your meetings with AI assistance, virtual audio routing, and smart meeting management</p>
</div>

---

A tool for automating Google Meet interactions with AI assistance. This project integrates with Google Meet and uses Vapi for audio/video processing.

## Prerequisites

### For Mac Users
1. Install PortAudio:
```bash
brew install portaudio
```

2. Install Python dependencies:
```bash
pip install -e requirements.txt
```

3. Install BlackHole (virtual audio device):
```bash
brew install blackhole-2ch
```

4. Restart your Mac after installation

### For Linux Users
1. Create a virtual audio sink:
```bash
# Create a null sink (virtual output/mic pair)
pactl load-module module-null-sink sink_name=blackhole
pactl load-module module-loopback source=blackhole.monitor
```

## Virtual Video Setup

### For Mac Users
1. Install OBS Studio:
   - Download from [OBS Studio GitHub](https://github.com/obsproject/obs-studio)
   - Note: Additional configuration may be required

### For Linux Users
1. Install and configure v4l2loopback:
```bash
sudo apt install v4l2loopback-dkms
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="VirtualCam" exclusive_caps=1
```

## Usage

1. Start the Vapi assistant:
```bash
cd virtual_sound_card
python blackhole_vapi.py
```

2. Connect to BlackHole for input/output devices in Google Meet

## Features

- Automated Google Meet joining
- AI-powered meeting assistance
- Virtual audio routing through BlackHole
- Virtual video support
- Meeting summarization and task tracking
- Email integration for follow-ups

## Development

The project consists of several components:
- Frontend: Next.js application
- Backend: FastAPI server
- Vapi Integration: Audio/video processing
- Virtual Sound Card: Audio routing
- Google Meet Integration: Meeting automation

## License

ISC
