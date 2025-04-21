# Czolg

## Install

On Raspberry Pi:

```bash
sudo apt update
sudo apt install -y python3-opencv
pip install --break-system-packages pymavlink
```

On PC:

```bash
uv sync
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
uv run viewer.py
```
