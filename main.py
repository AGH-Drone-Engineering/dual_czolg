import argparse
from pymavlink import mavutil

from czolg.mavlink_task import MavlinkTask


def main():
    parser = argparse.ArgumentParser(description='MAVLink Tank Controller')
    parser.add_argument('--tty', type=str, help='Enable TTY mode with the given path')
    parser.add_argument('--baudrate', type=int, help='Baudrate for TTY mode')
    parser.add_argument('--udpin', action='store_true', help='Enable UDPIN mode')
    parser.add_argument('--port', type=int, default=14550, help='Port for UDPIN mode')
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
    
    mavlink_task = MavlinkTask(connection)
    mavlink_task.start()

    try:
        mavlink_task.join()
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
