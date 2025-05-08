apt-get update
# For Playwright browsers:
apt-get install -y \
    libnss3 libxss1 libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libgtk-3-0 libgbm1 \
    libx11-xcb1 libxcb-dri3-0

# For PyAudio (PortAudio):
apt-get install -y portaudio19-dev

pip install playwright PyAudio

# Download browser binaries
python -m playwright install