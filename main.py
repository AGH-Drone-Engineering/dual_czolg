import argparse
from pymavlink import mavutil

from czolg.mavlink_task import MavlinkTask
from czolg.camera_task import CameraTask


def main():
    parser = argparse.ArgumentParser(description='MAVLink Tank Controller')

    parser.add_argument('--tty', type=str, help='Enable TTY mode with the given path')
    parser.add_argument('--baudrate', type=int, help='Baudrate for TTY mode')

    parser.add_argument('--udpin', action='store_true', help='Enable UDPIN mode')
    parser.add_argument('--port', type=int, default=14550, help='Port for UDPIN mode')

    parser.add_argument('--camera-viewer-ip', type=str, help='IP address of the camera viewer')
    parser.add_argument('--camera-viewer-port', type=int, default=5000, help='Port of the camera viewer')

    parser.add_argument('--camera-preview', action='store_true', help='Enable camera preview')

    args = parser.parse_args()

    connection = None

    if args.tty and args.udpin:
        print("Error: Cannot specify both TTY and UDPIN modes")
        return

    if args.tty:
        if not args.baudrate:
            print("Error: --baudrate is required when using TTY mode")
            return
        connection = mavutil.mavlink_connection(args.tty, baud=args.baudrate)
    elif args.udpin:
        if not args.port:
            print("Error: --port is required when using UDPIN mode")
            return
        connection = mavutil.mavlink_connection(f'udpin:0.0.0.0:{args.port}')
    else:
        print("Error: --tty or --udpin is required")
        return

    if not connection:
        print("Error: Invalid connection parameters")
        return

    if not args.camera_viewer_ip:
        print("Warning: --camera-viewer-ip is not set, camera stream will not be sent")

    camera_task = CameraTask(args.camera_viewer_ip, args.camera_viewer_port, args.camera_preview)
    mavlink_task = MavlinkTask(connection, camera_task)

    camera_task.start()
    mavlink_task.start()

    camera_task.join()
    mavlink_task.join()


if __name__ == "__main__":
    main()
