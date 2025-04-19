from pymavlink import mavutil
import time
import threading


class MavlinkTask:
    def __init__(self, connection, camera_task):
        self.connection = connection
        self.camera_task = camera_task
        self.thread = threading.Thread(target=self.task)

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def request_gps_data(self):
        """Request GPS data streams from the vehicle using SET_MESSAGE_INTERVAL"""
        print("Requesting GLOBAL_POSITION_INT data...")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # Command ID
            0,                         # Confirmation
            33,                        # Message ID for GLOBAL_POSITION_INT
            100000,                    # Interval in microseconds (10 Hz)
            0, 0, 0, 0, 0              # Unused parameters
        )

    def handle_gps_data(self, msg):
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

            self.camera_task.update_position(msg)

    def task(self):
        print("Waiting for heartbeat...")
        self.connection.wait_heartbeat()
        print("Heartbeat from system (system %u component %u)" %
            (self.connection.target_system, self.connection.target_component))

        self.request_gps_data()
        last_gps_message_time = time.time()

        try:
            while True:
                msg = self.connection.recv_match(
                    type='GLOBAL_POSITION_INT',
                    blocking=True,
                    timeout=1.0
                )

                current_time = time.time()

                if current_time - last_gps_message_time > 5:
                    print("No GPS data received for 5 seconds. Re-requesting data...")
                    self.request_gps_data()
                    last_gps_message_time = current_time

                if msg:
                    last_gps_message_time = current_time
                    self.handle_gps_data(msg)

        finally:
            self.connection.close()
