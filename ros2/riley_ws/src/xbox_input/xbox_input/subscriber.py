#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from riley_interfaces.msg import XboxInput

class XboxInputSubscriber(Node):

    def __init__(self):
        super().__init__('xbox_input_subscriber')
        self.subscription = self.create_subscription(XboxInput, 'xbox_input', self.listener_callback, 10)

    def listener_callback(self, msg):
        self.get_logger().info('Publishing: vel_l: %f, vel_r: %f, motor_state: %d, robot_id: %d' % (msg.vel_l, msg.vel_r, msg.motor_state, msg.robot_id))


def main(args=None):
    rclpy.init(args=args)

    xbox_subscriber = XboxInputSubscriber()

    rclpy.spin(xbox_subscriber)

    xbox_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()