import sounddevice as sd
import numpy as np

def callback(indata, frames, time, status):
    # Calculate audio intensity (RMS)
    rms = np.sqrt(np.mean(indata**2))
    
    # Convert to decibels with reference to full scale (dBFS)
    # Add small epsilon to avoid log(0)
    db = 20 * np.log10(max(rms, 1e-7))
    
    # Create a simple meter
    meter_length = 40
    filled = int((db + 60) / 60 * meter_length)  # Map -60dB to 0dB to meter length
    filled = max(0, min(meter_length, filled))  # Clamp values
    meter = "[" + "=" * filled + " " * (meter_length - filled) + "]"
    
    # Hook: Send this audio somewhere else (WebSocket, process, save)
    print(f"Audio frame: {indata.shape}, Intensity: {db:.2f} dB {meter}")

# Find the correct device index for 'BlackHole'
blackhole_index = None
for i, dev in enumerate(sd.query_devices()):
    if 'BlackHole' in dev['name']:
        blackhole_index = i
        break

if blackhole_index is None:
    print("BlackHole device not found!")
    exit(1)

# Record from it
with sd.InputStream(device=blackhole_index, channels=2, samplerate=44100, callback=callback):
    print("Listening...")
    sd.sleep(10000)

# Play back some audio to BlackHole output
# Generate a tone instead of white noise
duration = 2  # seconds
frequency = 440  # Hz (A4 note)
t = np.linspace(0, duration, int(44100 * duration), False)
audio = 0.5 * np.sin(2 * np.pi * frequency * t)  # 0.5 amplitude sine wave
audio = np.column_stack((audio, audio))  # Make stereo
sd.play(audio, samplerate=44100, device=blackhole_index)
sd.wait()