import time
import socket
from picamera2 import Picamera2, MappedArray
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
import cv2
import threading
import os
import json


class CameraTask:
    def __init__(self, remote_ip: str, remote_port: int, preview: bool):
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.preview = preview

        self.picam2 = Picamera2()
        self.picam2.post_callback = self.post_callback
        video_config = self.picam2.create_video_configuration(
            main={"format": "YUV420"},
            buffer_count=2,
            queue=False,
        )
        self.picam2.configure(video_config)
        self.encoder = H264Encoder(bitrate=1_000_000, repeat=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stream = None

        self.root_log_dir = "logs"
        self.log_dir = os.path.join(self.root_log_dir, time.strftime("%Y-%m-%d_%H-%M-%S"))
        os.makedirs(self.log_dir)

        self.last_position_timestamp = None
        self.last_position = None

        self.thread = threading.Thread(target=self.task)

    def start(self):
        self.picam2.start(show_preview=self.preview)
        if self.remote_ip:
            self.sock.connect((self.remote_ip, self.remote_port))
            self.stream = self.sock.makefile("wb")
            self.picam2.start_recording(self.encoder, FileOutput(self.stream))
        self.thread.start()

    def join(self):
        self.thread.join()

    def update_position(self, position):
        self.last_position_timestamp = time.time()
        self.last_position = position

    def post_callback(self, request):
        timestamp = time.strftime("%Y-%m-%d %X")
        colour = (0, 255, 0)
        origin = (0, 30)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1
        thickness = 2
        with MappedArray(request, "main") as m:
            cv2.putText(m.array, timestamp, origin, font, scale, colour, thickness)

    def task(self):
        try:
            frame_number = 0
            while True:
                image = self.picam2.capture_array()
                cv2.imwrite(os.path.join(self.log_dir, f"{frame_number:06d}.jpg"), image)
                with open(os.path.join(self.log_dir, f"{frame_number:06d}.json"), "w") as f:
                    json.dump({
                        "image_timestamp": time.time(),
                        "position_timestamp": self.last_position_timestamp,
                        "position": self.last_position,
                    }, f)
                frame_number += 1
        finally:
            self.picam2.stop_recording()
