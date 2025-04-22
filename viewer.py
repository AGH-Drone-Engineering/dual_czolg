import cv2
import socket
import numpy as np


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 5000))

    cv2.namedWindow("Camera", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_NORMAL)

    while True:
        data, addr = sock.recvfrom(65507)
        jpeg_buf = np.frombuffer(data, dtype=np.uint8)
        image = cv2.imdecode(jpeg_buf, cv2.IMREAD_COLOR)
        try:
            cv2.imshow("Camera", image)
        except cv2.error:
            pass
        if cv2.waitKey(1) & 0xFF == 27:
            break


if __name__ == "__main__":
    main()
