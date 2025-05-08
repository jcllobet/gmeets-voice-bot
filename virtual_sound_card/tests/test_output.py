import sounddevice as sd
import numpy as np
import sys

# Generate 2 sec of sine wave
samplerate = 44100
duration = 2
freq = 440
t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
audio = 1 * np.sin(2 * np.pi * freq * t).astype(np.float32)

# Print available audio devices
print("Available audio devices:")
for i, dev in enumerate(sd.query_devices()):
    print(f"{i}: {dev['name']} (Outputs: {dev['max_output_channels']}, Inputs: {dev['max_input_channels']})")

# Try to find BlackHole device
blackhole_found = False
for i, dev in enumerate(sd.query_devices()):
    if 'BlackHole' in dev['name'] and dev['max_output_channels'] > 0:
        device_index = i
        blackhole_found = True
        print(f"\nFound BlackHole device at index {device_index}: {dev['name']}")
        
        # Send to BlackHole virtual device
        print(f"Playing audio through BlackHole for {duration} seconds...")
        print("Note: You won't hear this directly - it's being sent to the virtual device.")
        print("Make sure another application is set to record from BlackHole.")
        sd.play(audio, samplerate=samplerate, device=device_index)
        sd.wait()
        break

if not blackhole_found:
    print("\nNo BlackHole device found. Would you like to play through your default speakers instead? (y/n)")
    choice = input().lower()
    if choice == 'y':
        print("Playing through default speakers...")
        sd.play(audio, samplerate=samplerate)
        sd.wait()
    else:
        print("To use BlackHole, make sure it's installed and properly configured.")
        print("You can download it from: https://existential.audio/blackhole/")
        sys.exit(1)
