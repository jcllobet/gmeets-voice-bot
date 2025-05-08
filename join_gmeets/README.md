# gmeets-joiner

[Link](https://chatgpt.com/share/6802e1a1-c484-8004-8ef9-ed381055aad0)

# Instructions

```bash
sudo apt update
sudo apt install -y pipewire pipewire-pulse wireplumber pipewire-alsa pipewire-jack libpulse-dev libasound2-dev ffmpeg build-essential python3 python3-pip xvfb

```


In a venv:

Python Packages: Install Playwright, PyAudio (for audio capture/playback), and any OpenAI/WebSocket clients:

```bash
pip3 install playwright websockets pyaudio
```

Then

```bash
playwright install chromium
```

# Enable Pipewire at Login

```bash
systemctl --user enable pipewire.service pipewire-pulse.service wireplumber.service
systemctl --user start pipewire.service pipewire-pulse.service wireplumber.service
```

We can check if it's running with:

```bash
pactl info | grep "Server Name"
```

# Create a virtual speaker sync and audio source:

```bash
# 1. Create a virtual speaker (audio sink)
pactl load-module module-null-sink \
    media.class=Audio/Sink \
    sink_name=meet_sink \
    channel_map=stereo \
    sink_properties=device.description="Virtual Speaker (Meet)"

# 2. Create a virtual microphone (audio source)
pactl load-module module-null-sink \
    media.class=Audio/Source/Virtual \
    sink_name=meet_mic \
    channel_map=front-left,front-right \
    sink_properties=device.description="Virtual Mic (Meet)"
```

- Verify synks are present (should be in suspended state):

```bash
pactl list short sinks    # should include meet_sink
pactl list short sources  # should include meet_mic and meet_sink.monitor
```

- Create a 3rd sink for ai output so that this way we don't send gmeet audio iunto the mic which would create an echo/loop:

```bash
pactl load-module module-null-sink \
    media.class=Audio/Sink \
    sink_name=ai_sink \
    channel_map=stereo \
    sink_properties=device.description="Virtual Speaker (AI Voice)"
```

- **Route the AI Sink into the Virtual Mic**: Now link the AI sink’s monitor to the virtual microphone input. This ensures any audio played to ai_sink ends up as input on `meet_mic`:

```bash
# Link AI sink monitor (both left and right channels) to virtual mic input
pw-link ai_sink:monitor_FL meet_mic:input_FL 
pw-link ai_sink:monitor_FR meet_mic:input_FR

```

-**Tip**: The above module loads are not permanent; they will disappear on reboot or if PipeWire restarts. To make them persistent, you can add these module lines to your PipeWire configuration (e.g., in ~/.config/pipewire/pipewire-pulse.conf.d/virtual-devices.conf). For now, running the commands manually (or via a startup script) is fine for testing.

- **Set the Default Audio Sinks (if needed)**: By default, new audio streams go to the system default sink/source. We will manually direct specific clients (browser and our Python script) to use our virtual devices, so changing the global default may not be necessary. However, for convenience you can set the default output to the AI sink while running the agent:

```bash
pactl set-default-sink ai_sink
pactl set-default-source meet_mic
```


- Install XQuartz
- Open xQuartz

```bash
  open -a XQuartz
```

- `XQuartz > Preferences > Security`
- Make sure "Allow connections from network clients" is checked.

- export xhost to path:
```bash
export PATH="/opt/X11/bin:$PATH"
```

```bash
xhost + 127.0.0.1
```

 - Now open a terminal in ssh and run:
 ```bash
 ssh -Y -i ~/.ssh/azure_gmeets_agent.pem azureuser@20.51.233.110
 ```

 - Create a virtual speaker (null sink).  
 - Identify its monitor source
 - Congigure chrome to use our virtual speaker for output and the virtual's speaker monitor for input.

 ```bash
     # Load a null sink module, naming it 'meet_output'
    pactl load-module module-null-sink sink_name=meet_output sink_properties=device.description="Meet_Virtual_Speaker"

    # (Optional but recommended) Check that the sink and its monitor source were created:
    pactl list sinks short | grep 'meet_output'
    pactl list sources short | grep 'meet_output.monitor' 
```