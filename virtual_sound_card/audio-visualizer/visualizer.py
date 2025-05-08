import colorsys
import numpy as np
import pyvirtualcam
import pyaudio
import struct
import time
import scipy.fft

# Audio settings
CHUNK = 1024 * 2     # Number of audio samples per frame
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100         # Audio sampling rate
DEVICE_NAME = "MacBook Air Microphone"  # Target audio input device

# Visualization settings
WIDTH = 1280
HEIGHT = 720
FPS = 30
BAR_COUNT = 50       # Number of frequency bars
BAR_WIDTH = WIDTH // BAR_COUNT
MAX_AMPLITUDE = 2**15  # Maximum amplitude for 16-bit audio

def find_input_device(p, device_name):
    """Find the device index for a given device name"""
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_name in device_info['name'] and device_info['maxInputChannels'] > 0:
            return i
    print(f"Device {device_name} not found. Available devices:")
    for i in range(p.get_device_count()):
        print(f"{i}: {p.get_device_info_by_index(i)['name']}")
    return None

def get_frequency_spectrum(audio_data, chunk_size, rate):
    """Calculate the frequency spectrum from audio data"""
    fft_result = scipy.fft.rfft(audio_data)
    freq_amplitudes = np.abs(fft_result) / chunk_size
    # Only take the first half as the second half is the mirror image
    return freq_amplitudes[:chunk_size//2]

def main():
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # Find Blackhole device
    device_index = find_input_device(p, DEVICE_NAME)
    if device_index is None:
        print("Using default input device")
        device_index = p.get_default_input_device_info()['index']
    
    # Open audio stream
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=device_index
    )
    
    print(f"Audio input initialized. Using device: {p.get_device_info_by_index(device_index)['name']}")
    
    # Initialize virtual camera
    with pyvirtualcam.Camera(width=WIDTH, height=HEIGHT, fps=FPS) as cam:
        print(f'Using virtual camera: {cam.device}')
        frame = np.zeros((cam.height, cam.width, 3), dtype=np.uint8)  # RGB
        
        try:
            while True:
                # Read audio data
                audio_data = stream.read(CHUNK, exception_on_overflow=False)
                
                # Convert audio data to numpy array
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                # Get frequency spectrum
                spectrum = get_frequency_spectrum(audio_array, CHUNK, RATE)
                
                # Reshape spectrum to fit our bar count (use logarithmic scale for better visualization)
                indices = np.logspace(0, np.log10(len(spectrum)), BAR_COUNT, base=10, dtype=np.int32)
                bars_height = [np.mean(spectrum[indices[i]:indices[i+1]]) for i in range(len(indices)-1)]
                
                # Normalize heights to fit the screen
                max_height = max(1, max(bars_height))
                bars_height = [int((h / max_height) * (HEIGHT * 0.8)) for h in bars_height]
                
                # Create visualization frame
                frame.fill(0)  # Clear the frame
                
                # Draw frequency bars
                for i, height in enumerate(bars_height):
                    # Use hue based on frequency and brightness based on amplitude
                    h = i / BAR_COUNT  # Hue from 0 to 1
                    s = 1.0  # Full saturation
                    v = min(1.0, height / (HEIGHT * 0.4))  # Brightness based on amplitude
                    
                    r, g, b = colorsys.hsv_to_rgb(h, s, v)
                    x_pos = i * BAR_WIDTH
                    
                    # Draw the bar
                    frame[HEIGHT - height:HEIGHT, x_pos:x_pos + BAR_WIDTH] = [int(r * 255), int(g * 255), int(b * 255)]
                
                # Add a reflection effect
                reflection = frame.copy()
                reflection = np.flipud(reflection) * 0.3  # Flip vertically and make it dimmer
                frame[:HEIGHT//2, :] = np.maximum(frame[:HEIGHT//2, :], reflection[HEIGHT//2:, :])
                
                # Send frame to virtual camera
                cam.send(frame)
                cam.sleep_until_next_frame()
                
        except KeyboardInterrupt:
            print("Visualizer stopped by user")
        finally:
            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == "__main__":
    main()
