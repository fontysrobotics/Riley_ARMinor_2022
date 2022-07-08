import rclpy
from rclpy.node import Node
from imu_sensor.registers import *
from imu_sensor.mpu_9250 import MPU9250
from riley_interfaces.msg import IMUSensor

import sys
sys.path.append("/home/ubuntu/riley_ws")
import global_constants


class IMUSensorPublisher(Node):
    
    def __init__(self):
        # Configure the MPU9250 IMU sensor module
        self.mpu = MPU9250(
            # address_ak=AK8963_ADDRESS, 
            address_mpu_master=MPU9050_ADDRESS_68, # In 0x68 Address
            address_mpu_slave=None, 
            bus=1,
            gfs=GFS_1000, 
            afs=AFS_8G, 
            # mfs=AK8963_BIT_16, 
            # mode=AK8963_MODE_C100HZ
            )
        self.mpu.configure() # Apply the settings to the registers
        
        super().__init__('imu_sensor_publisher')
        self.publisher = self.create_publisher(IMUSensor, 'imu_sensor', 10)
        timer_period = 0.2  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        # Read values and create message
        msg = IMUSensor()
        gyroXYZ = self.mpu.readGyroscopeMaster()    # Get gyroscope values in 3 axis
        accXYZ = self.mpu.readAccelerometerMaster() # Get accelerometer values in 3 axis
        tempC = self.mpu.readTemperatureMaster()    # Get temperature reading in degrees Celsius
        msg.gyro.x = float(gyroXYZ[0])
        msg.gyro.y = float(gyroXYZ[1])
        msg.gyro.z = float(gyroXYZ[2])
        msg.accel.x = float(accXYZ[0])
        msg.accel.y = float(accXYZ[1])
        msg.accel.z = float(accXYZ[2])
        msg.temp = float(tempC)
        msg.robot_id = global_constants.RILEY_ROBOT_ID
        
        # Publish message to topic
        self.publisher.publish(msg)
        self.get_logger().info( \
            "Publishing:\nGyroscope:\nX: %f\nY: %f\nZ: %f\nAccelerometer:\nX: %f\nY: %f\nZ: %f\nTemperature: %f C\nRobot ID: %d" % \
            (msg.gyro.x, msg.gyro.y, msg.gyro.z, msg.accel.x, msg.accel.y, msg.accel.z, msg.temp, msg.robot_id))


def main(args=None):
    rclpy.init(args=args)

    imu_sensor_publisher = IMUSensorPublisher()

    rclpy.spin(imu_sensor_publisher)
    
    imu_sensor_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
