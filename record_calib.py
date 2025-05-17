from picamera2 import Picamera2
from libcamera import Transform
import cv2
import os
import argparse


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=str)
    args = parser.parse_args()

    if os.path.exists(args.output_dir):
        print(f"Output directory {args.output_dir} already exists")
        return
    os.makedirs(args.output_dir)

    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(
        main={"size": (3280, 2464), "format": "BGR888"},
        raw={"size": (3280, 2464)},
        controls={"FrameRate": 30},
        transform=Transform(hflip=1, vflip=1),
    )
    picam2.configure(video_config)
    picam2.start()

    frame_count = 0

    while True:
        frame = picam2.capture_array("main")
        lores = cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2), interpolation=cv2.INTER_AREA)
        cv2.imshow("Preview", lores)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('s'):
            cv2.imwrite(os.path.join(args.output_dir, f"{frame_count:06d}.png"), frame)
            frame_count += 1
            print(f"Saved frame {frame_count}")


if __name__ == "__main__":
    main()
