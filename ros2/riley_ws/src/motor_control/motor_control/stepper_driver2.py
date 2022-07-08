import time
from threading import Thread
from time import sleep

import rclpy
import RPi.GPIO as GPIO
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from riley_interfaces.msg import IMUSensor, TOFSensor, XboxInput

from motor_control.pid import PID


class stepperMotorDriver(Node):
    def __init__(self):
        super().__init__('Stepper_Driver_2')
        # Multithreading settings
        self.group1 = MutuallyExclusiveCallbackGroup()
        self.group2 = MutuallyExclusiveCallbackGroup()
        self.group3 = MutuallyExclusiveCallbackGroup()
        
        self.get_logger().info('Creating a subscriber to xbox controller now')
        self.subscription = self.create_subscription(XboxInput, 'xbox_input', self.controller_callback, 10, callback_group=self.group1)
        
        self.get_logger().info('Creating a subscriber to IMU sensor data now')
        self.subscriptionIMU = self.create_subscription(IMUSensor, 'imu_sensor', self.IMU, 10, callback_group=self.group2)
        
        self.get_logger().info('Creating a subscriber to TOF sensor data now')
        self.subscriptionTOF = self.create_subscription(TOFSensor, 'tof_sensor', self.TOF, 10, callback_group=self.group3)  
                
        # GPIO pins used
        self.StepperEnable = 5                  # Enable pin of the motors
        self.StepperRightDIR = 6                # Direction of motor 1
        self.StepperRightSTEP = 12              # Step of motor 1
        self.StepperLeftDIR = 26                # Direction of motor 2
        self.StepperLeftSTEP = 13               # Step of motor 2
        self.MODE = (22, 23, 24)                # Microstep Resolution GPIO Pins
        
        # Variables
        self.CW = 0                             # Clockwise Rotation
        self.CCW = 1                            # Counterclockwise Rotation
        self.SPR = 1                            # Steps per Revolution (360 / 7.5)
        self.startup_right = 0.1                # Starting speed
        self.startup_left = 0.1                 # Starting speed
        self.kp = 0.25                          # Proportional gain
        self.vel_limits = (0, 10.0)             # Speed limits
        self.delay_limits = (0.0003, 0.005)     # "Delay" limits where delay is time to wait (not using delays)
        self.speed_delay_left = 1               # The actual "delay" the motors are stepping in
        self.speed_delay_right = 1              # The actual "delay" the motors are stepping in
        
        self.print_flag = 0                     # Debug print cap flag
        
        self.flipping_time = 0                  # Last time flip was detected
        self.gap_time = 0                       # Last time a gap was detected
        self.obs_time = 0                       # Last time an obstacle was detected
        
        self.l_dir = self.CCW
        self.r_dir = self.CW
        self.right_wheel = PID(kp=self.kp, updateTime=0)
        self.left_wheel = PID(kp=self.kp, updateTime=0)
        self.result_right = 0
        self.result_left = 0
        
        
        self.flip = False                       # Flip detected flag
        self.gap = False                        # Gap detected flag
        self.obs = False                        # Obstacle detected flag
    
        # Setup of GPIO pins of the Raspberry
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.StepperEnable, GPIO.OUT)
        GPIO.setup(self.StepperLeftDIR, GPIO.OUT)
        GPIO.setup(self.StepperLeftSTEP, GPIO.OUT)
        GPIO.setup(self.StepperRightDIR, GPIO.OUT)
        GPIO.setup(self.StepperRightSTEP, GPIO.OUT)
        GPIO.setup(self.MODE, GPIO.OUT)
        RESOLUTION = {'Full': (0, 0, 0),
                    'Half': (1, 0, 0),
                    '1/4': (0, 1, 0),
                    '1/8': (1, 1, 0),
                    '1/16': (0, 0, 1),
                    '1/32': (1, 0, 1)}
        GPIO.output(self.MODE, RESOLUTION['1/4'])
        
        
    # must be run in a seperate Thread
    def LeftMotor(self):
        self.get_logger().info('Starting left Steppermotor')
        while True:
            # print("LEFT {}".format(self.speed_delay_left))
            if self.speed_delay_left < self.delay_limits[1] * 0.98: 
                GPIO.output(self.StepperLeftDIR, self.l_dir)
                GPIO.output(self.StepperLeftSTEP, GPIO.HIGH)
                sleep(self.speed_delay_left/4)
                GPIO.output(self.StepperLeftSTEP, GPIO.LOW)
                sleep(self.speed_delay_left)
                # print("Left {}".format(self.speed_delay_left))
        
    # must be run in a seperate Thread
    def RightMotor(self):
        self.get_logger().info('Starting right Steppermotor')
        while True:
            # print("RIGHT {}".format(self.speed_delay_right))
            if self.speed_delay_right < self.delay_limits[1] * 0.98: 
                GPIO.output(self.StepperRightDIR,  self.r_dir)
                GPIO.output(self.StepperRightSTEP, GPIO.HIGH)
                sleep(self.speed_delay_right/4)
                GPIO.output(self.StepperRightSTEP, GPIO.LOW)
                sleep(self.speed_delay_right)
                # print("Right {}".format(self.speed_delay_right))
            
    
    def controller_callback(self, msg : XboxInput):        
        if (self.startup_right * 0.95 != msg.vel_r or self.startup_left * 0.95 != msg.vel_l) and self.enable_steppers(msg.motor_state):
            if self.flip:
                print("FLIP!")
                self.startup_right -= self.right_wheel.compute(abs(5), self.startup_right)
                self.startup_left -= self.left_wheel.compute(abs(5), self.startup_left)
                self.r_dir = self.CW
                self.l_dir = self.CCW
                
            elif self.gap:
                print("GAP!")
                self.startup_right -= self.right_wheel.compute(abs(4), self.startup_right)
                self.startup_left -= self.left_wheel.compute(abs(4), self.startup_left)
                self.r_dir = self.CCW
                self.l_dir = self.CW
                
            elif self.obs:
                print("OBSTICAL!")
                self.startup_right -= self.right_wheel.compute(abs(4), self.startup_right)
                self.startup_left -= self.left_wheel.compute(abs(4), self.startup_left)
                self.r_dir = self.CCW
                self.l_dir = self.CW
                
            else:
                if  msg.vel_r > 0:
                    self.r_dir = self.CW
                    # print("FORWARD RIGHT")
                    
                elif msg.vel_r < 0:
                    self.r_dir = self.CCW
                    # print("BACKWARD RIGHT")
                    
                if msg.vel_l > 0:
                    self.l_dir = self.CCW
                    # print("FORWARD LEFT")
                    
                elif msg.vel_l < 0: 
                    self.l_dir = self.CW
                    # print("BACKWARD LEFT")
                
                if abs(msg.vel_r) >= 9.0:
                    self.startup_right -= self.right_wheel.compute(abs(msg.vel_r), self.startup_right)
                    self.startup_left -= self.left_wheel.compute(abs(msg.vel_r), self.startup_left)
                else:
                    self.startup_right -= self.right_wheel.compute(abs(msg.vel_r), self.startup_right)
                    self.startup_left -= self.left_wheel.compute(abs(msg.vel_l), self.startup_left)
              
                
            self.result_right = self.startup_right
            self.result_left = self.startup_left
            
            self.speed_delay_left = self.map(self.result_left, self.vel_limits[0], self.vel_limits[1], self.delay_limits[1], self.delay_limits[0])
            self.speed_delay_right = self.map(self.result_right, self.vel_limits[0], self.vel_limits[1], self.delay_limits[1], self.delay_limits[0])
            
        if self.print_flag > 10:
            print("Input (left, right): \t\t\t{0},\t{1}".format(msg.vel_l, msg.vel_r))
            print("PID right:\t{}".format(self.result_right)) 
            print("PID left:\t\t{}".format(self.result_left))
            print("Motorstate: \t\t\t\t\t\t\t\t\t\t{}".format(msg.motor_state))
            
            self.print_flag = 0
        
        elif self.print_flag <= 10:
            self.print_flag += 1


    def IMU(self, msg : IMUSensor):
        now = time.monotonic()
        if msg.gyro.x > 100:
            print("Tilting {}".format(msg.gyro.x))
            self.flip = True
            self.flipping_time = now
            
        elif now - self.flipping_time >= 0.5:
            # print("Tilting {}".format(msg.gyro.x))
            self.flip = False
            
                     
    def TOF(self, msg : TOFSensor):
        now = time.monotonic()
        if msg.dist_value > 250:
            print("Drop detected: {}".format(msg.dist_value))
            self.gap_time = now 
            self.gap = True
            
        elif msg.dist_value < 100 and msg.dist_value >= 0:
            print("Obstacle detected: {}".format(msg.dist_value))
            self.obs_time = now
            self.obs = True
            
        elif self.gap and now - self.gap_time >= 1:
            print("Done gap {}".format(msg.dist_value))
            self.gap = False
            
        elif self.obs and now - self.obs_time >= 1:
            print("Done obs {}".format(msg.dist_value))
            self.obs = False
            
            
    def map(self,value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan) 
        
        
    def enable_steppers(self, enable):
        if enable:
            GPIO.output(self.StepperEnable, GPIO.LOW)
            return True
        else:
            GPIO.output(self.StepperEnable, GPIO.HIGH)
            return False
    
            
def main(args=None):
    rclpy.init(args=args)

    try:
        # declare the node constructor
        stepperControl = stepperMotorDriver()
        
        # #enabling the lidar
        # LidarEnable = 18
        # GPIO.setup(LidarEnable, GPIO.OUT)
        # GPIO.output(LidarEnable, GPIO.HIGH)
        
        # start seperate threads for the stepper control and run them as daemons so it stops on ros exits
        right_motor = Thread(target=stepperControl.RightMotor, args=(), daemon=True)
        left_motor = Thread(target=stepperControl.LeftMotor, args=(), daemon=True)
       
        executor = MultiThreadedExecutor(num_threads=3)
        
        try:
            right_motor.start()
            left_motor.start()
            
            # pause the program execution, waits for a request to kill the node (ctrl+c)
            rclpy.spin(stepperControl, executor)
            
        finally:
            # #disabling the lidar
            # GPIO.output(LidarEnable, GPIO.LOW)
            stepperControl.destroy_node()

    finally:
        # shutdown the ROS communication
        rclpy.shutdown()
        
    
if __name__ == '__main__':
    main()
