import rclpy
from rclpy.node import Node
from riley_interfaces.msg import IMUSensor

class IMUSensorSubscriber(Node):
    
    def __init__(self):
        super().__init__('imu_sensor_subscriber')
        self.subscription = self.create_subscription(IMUSensor, 'imu_sensor', self.listener_callback, 10)

    def listener_callback(self, msg : IMUSensor):
        self.get_logger().info( \
            "Receiving:\nGyroscope:\nX: %f\nY: %f\nZ: %f\nAccelerometer:\nX: %f\nY: %f\nZ: %f\nTemperature: %f C\nRobot ID: %d" % \
            (msg.gyro.x, msg.gyro.y, msg.gyro.z, msg.accel.x, msg.accel.y, msg.accel.z, msg.temp, msg.robot_id))
        
        if msg.gyro.x > 15:
            self.get_logger().info("TILTING!")
            #Reduce Stepper power backwards
        if msg.accel.y > 0.3:
            self.get_logger().info("Collided!")
            # Stop and try to climb


def main(args=None):
    rclpy.init(args=args)

    imu_sensor_subscriber = IMUSensorSubscriber()

    rclpy.spin(imu_sensor_subscriber)

    imu_sensor_subscriber.destroy_node()
    rclpy.shutdown()