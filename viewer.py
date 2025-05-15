import cv2
import socket
import numpy as np
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-ip", type=str)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 5000))

    control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if args.target_ip:
        print(f"Sending control commands to {args.target_ip}:5001")
    control_address = (args.target_ip, 5001) if args.target_ip else None

    cv2.namedWindow("Camera", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_NORMAL)

    while True:
        data, addr = sock.recvfrom(65507)
        jpeg_buf = np.frombuffer(data, dtype=np.uint8)
        image = cv2.imdecode(jpeg_buf, cv2.IMREAD_COLOR)
        try:
            cv2.imshow("Camera", image)
        except cv2.error:
            pass

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        if control_address is not None:
            if key == ord('w') or key == ord('W'):
                control_sock.sendto(b"1", control_address)
            elif key == ord('s') or key == ord('S'):
                control_sock.sendto(b"-1", control_address)


if __name__ == "__main__":
    main()
