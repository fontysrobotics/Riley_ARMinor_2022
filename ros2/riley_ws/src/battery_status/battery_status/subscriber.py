import rclpy
from rclpy.node import Node
from riley_interfaces.msg import BatteryStatus

class BatteryStatusSubscriber(Node):
    
    def __init__(self):
        super().__init__('battery_status_subscriber')
        self.subscription = self.create_subscription(BatteryStatus, 'battery_status', self.listener_callback, 10)

    def listener_callback(self, msg : BatteryStatus):
        self.get_logger().info( \
            "Receiving:\nBus Voltage: %f V\nBus Current: %f mA\nPower: %f mW\nBattery level: %f%%\nRobot ID: %d" % \
            (msg.voltage, msg.current, msg.power, msg.battery_level, msg.robot_id))


def main(args=None):
    rclpy.init(args=args)

    battery_status_subscriber = BatteryStatusSubscriber()

    rclpy.spin(battery_status_subscriber)

    battery_status_subscriber.destroy_node()
    rclpy.shutdown()