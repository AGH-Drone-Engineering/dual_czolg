import argparse
from pymavlink import mavutil
import time


def request_gps_data(connection):
    """Request GPS data streams from the vehicle using SET_MESSAGE_INTERVAL"""
    print("Requesting GLOBAL_POSITION_INT data...")
    connection.mav.command_long_send(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # Command ID
        0,                         # Confirmation
        33,                        # Message ID for GLOBAL_POSITION_INT
        100000,                    # Interval in microseconds (10 Hz)
        0, 0, 0, 0, 0              # Unused parameters
    )


def handle_gps_data(msg):
    """Process and display GPS data from MAVLink messages"""
    if msg.get_type() == 'GLOBAL_POSITION_INT':
        print("GLOBAL_POSITION_INT:")
        print(f"  Time: {msg.time_boot_ms}")
        print(f"  Latitude: {msg.lat / 1e7} deg")
        print(f"  Longitude: {msg.lon / 1e7} deg")
        print(f"  Altitude (MSL): {msg.alt / 1000} m")
        print(f"  Altitude (relative): {msg.relative_alt / 1000} m")
        print(f"  Ground speed X: {msg.vx / 100} m/s")
        print(f"  Ground speed Y: {msg.vy / 100} m/s")
        print(f"  Ground speed Z: {msg.vz / 100} m/s")
        print(f"  Heading: {msg.hdg / 100} deg")
        print("-------------------------------------")


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

    print("Waiting for heartbeat...")
    connection.wait_heartbeat()
    print("Heartbeat from system (system %u component %u)" %
          (connection.target_system, connection.target_component))

    request_gps_data(connection)

    last_gps_message_time = time.time()

    try:
        while True:
            msg = connection.recv_match(
                type='GLOBAL_POSITION_INT',
                blocking=True,
                timeout=1.0
            )

            current_time = time.time()

            if current_time - last_gps_message_time > 5:
                print("No GPS data received for 5 seconds. Re-requesting data...")
                request_gps_data(connection)
                last_gps_message_time = current_time

            if msg:
                last_gps_message_time = current_time
                handle_gps_data(msg)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
