import rclpy
from rclpy.node import Node
from battery_status.ina226 import INA226
from riley_interfaces.msg import BatteryStatus

import sys
sys.path.append("/home/ubuntu/riley_ws")
import global_constants

BATMIN = 9          # When battery reaches 9V it's empty
BATMAX = 12.6       # When battery is charged it's 12.6V
BATOFFSET = 0.58    # The PCB gives the battery voltage an offset


class BatteryStatusPublisher(Node):
    
    def __init__(self):
        # Configure the INA226 power monitor module
        self.monitor_module = INA226(busnum=1, max_expected_amps=4)
        self.monitor_module.configure()
        
        super().__init__('battery_status_publisher')
        self.publisher = self.create_publisher(BatteryStatus, 'battery_status', 10)
        timer_period = 3  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        # Wake monitor module from low power state
        self.monitor_module.wake(3)
        
        # Read values and create message
        msg = BatteryStatus()
        msg.voltage = float(self.monitor_module.voltage()) # V
        msg.current = float(self.monitor_module.current()) # mA
        msg.power = float(self.monitor_module.power()) # mW
        msg.battery_level = float(100 * ((msg.voltage + BATOFFSET - BATMIN) / (BATMAX - BATMIN))) # Percent
        msg.robot_id = global_constants.RILEY_ROBOT_ID
        
        # Publish message to topic
        self.publisher.publish(msg)
        self.get_logger().info( \
            "Publishing:\nBus Voltage: %f V\nBus Current: %f mA\nPower: %f mW\nBattery level: %f%%\nRobot ID: %d" % \
            (msg.voltage, msg.current, msg.power, msg.battery_level, msg.robot_id))
        
        # Place monitor back into low power state
        self.monitor_module.sleep()


def main(args=None):
    rclpy.init(args=args)

    battery_status_publisher = BatteryStatusPublisher()

    rclpy.spin(battery_status_publisher)
    
    battery_status_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
