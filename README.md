# Czolg

## Install

```bash
sudo apt update
sudo apt install -y python3-opencv
pip install --break-system-packages pymavlink
```

## Run

Remote preview:

```bash
python main.py --tty /dev/ttyAMA0 --baudrate 57600 --camera-viewer-ip <your-ip>
```

Local preview:

```bash
python main.py --tty /dev/ttyAMA0 --baudrate 57600 --camera-preview
```

## View camera

```bash
gst-launch-1.0 udpsrc address=0.0.0.0 port=5000 ! h264parse ! queue ! avdec_h264 ! autovideosink sync=false
```
