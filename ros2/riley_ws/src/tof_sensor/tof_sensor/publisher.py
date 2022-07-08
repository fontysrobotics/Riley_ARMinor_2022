import rclpy
from rclpy.node import Node
from riley_interfaces.msg import TOFSensor
import VL53L1X

import sys
sys.path.append("/home/ubuntu/riley_ws")
import global_constants

# 0 = Unchanged, 1 = Short Range, 2 = Medium Range, 3 = Long Range
TOF_RANGE_MODE = 1

class TOFSensorPublisher(Node):
    
    def __init__(self):
        # Configure the VL53L1X TOF sensor module
        
        self.tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        self.tof.open()
        self.tof.set_timing(66000, 70)
        self.tof.start_ranging(TOF_RANGE_MODE)
        
        super().__init__('tof_sensor_publisher')
        self.publisher = self.create_publisher(TOFSensor, 'tof_sensor', 10)
        timer_period = 0.2 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        # Read values and create message
        msg = TOFSensor()
        msg.dist_value = int(self.tof.get_distance())
        msg.robot_id = global_constants.RILEY_ROBOT_ID
        
        # Publish message to topic
        self.publisher.publish(msg)
        self.get_logger().info("Publishing:\nDistance value: %d\nRobot ID: %d" % (msg.dist_value, msg.robot_id))


def main(args=None):
    rclpy.init(args=args)

    tof_sensor_publisher = TOFSensorPublisher()

    rclpy.spin(tof_sensor_publisher)
    
    tof_sensor_publisher.tof.stop_ranging()
    tof_sensor_publisher.tof.close()
    tof_sensor_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
