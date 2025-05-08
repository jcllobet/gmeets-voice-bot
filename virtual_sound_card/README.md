For Mac do:
```
brew install blackhole-2ch
```
then restart mac.

For Linux do:
```
# Create a null sink (virtual output/mic pair)
pactl load-module module-null-sink sink_name=blackhole
pactl load-module module-loopback source=blackhole.monitor
```

Run 
```
python blackhole_vapi.py
```
and connect to blackhole for input/output devices in gmeets.


For virtual video:

on mac:
Install https://github.com/obsproject/obs-studio

on Linux:
```
sudo apt install v4l2loopback-dkms
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="VirtualCam" exclusive_caps=1
```

push video using: https://github.com/letmaik/pyvirtualcam
