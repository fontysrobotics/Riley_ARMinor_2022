import rclpy
from rclpy.node import Node
from riley_interfaces.msg import TOFSensor

class TOFSensorSubscriber(Node):
    
    def __init__(self):
        super().__init__('tof_sensor_subscriber')
        self.subscription = self.create_subscription(TOFSensor, 'tof_sensor', self.listener_callback, 10)

    def listener_callback(self, msg : TOFSensor):
        self.get_logger().info("Receiving:\nDistance value: %d\nRobot ID: %d" % (msg.dist_value, msg.robot_id))


def main(args=None):
    rclpy.init(args=args)

    tof_sensor_subscriber = TOFSensorSubscriber()

    rclpy.spin(tof_sensor_subscriber)

    tof_sensor_subscriber.destroy_node()
    rclpy.shutdown()