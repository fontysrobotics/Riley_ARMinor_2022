#!/usr/bin/env python3
from cmath import pi
from time import monotonic, sleep

import rclpy
import RPi.GPIO as GPIO
from rclpy.constants import S_TO_NS
from rclpy.node import Node
from riley_interfaces.msg import XboxInput

from motor_control.pid import PID

class stepperMotorDriver(Node):

    def __init__(self):
        super().__init__('xbox_controller_subscriber')
        self.get_logger().info('Creating a subscriber to xbox controller now')
        self.subscription = self.create_subscription(XboxInput, 'xbox_input', self.listener_callback, 10)
        
        
        self.accelerating = False
        self.call_counter = 0
        self.current_speed = 0.0
        
        # pin values
        self.StepperRightDIR = 6     # Direction of motor 1
        self.StepperRightSTEP = 5    # Step of motor 1
        self.StepperLeftDIR = 26     # Direction of motor 2
        self.StepperLeftSTEP = 16    # Step of motor 2
        self.MODE = (22, 23, 24)     # Microstep Resolution GPIO Pins

        # GPIO pinmode init 
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.StepperLeftDIR, GPIO.OUT)
        GPIO.setup(self.StepperLeftSTEP, GPIO.OUT)
        GPIO.setup(self.StepperRightDIR, GPIO.OUT)
        GPIO.setup(self.StepperRightSTEP, GPIO.OUT)
        GPIO.setup(self.MODE, GPIO.OUT)

        # stepper driver mode select
        self.RESOLUTION = {'Full': (0, 0, 0),
                    'Half': (1, 0, 0),
                    '1/4': (0, 1, 0),
                    '1/8': (1, 1, 0),
                    '1/16': (0, 0, 1),
                    '1/32': (1, 0, 1)}
        self.used_resolution = '1/4'
        GPIO.output(self.MODE, self.RESOLUTION[self.used_resolution])

        # Declarations
        if   self.used_resolution == 'Full': self.SPR = 2 * pi / (1.8 * pi/180)             # Steps per Revolution (200)
        elif self.used_resolution == 'Half': self.SPR = 2 * pi / (1.8 * pi/180) / (1/2)     # Steps per Revolution (400)
        elif self.used_resolution == '1/4':  self.SPR = 2 * pi / (1.8 * pi/180) / (1/4)     # Steps per Revolution (800)
        elif self.used_resolution == '1/8':  self.SPR = 2 * pi / (1.8 * pi/180) / (1/8)     # Steps per Revolution (1600)
        elif self.used_resolution == '1/16': self.SPR = 2 * pi / (1.8 * pi/180) / (1/16)    # Steps per Revolution (3200)
        elif self.used_resolution == '1/32': self.SPR = 2 * pi / (1.8 * pi/180) / (1/32)    # Steps per Revolution (6400)
        # print("Steps per revolution: {}".format(SPR))
        self.RFW = False      # Clockwise Rotation
        self.LFW = True     # Counterclockwise Rotation

        # Variables
        self.step_count = 0
        self.last_step_count = 0
        self.last_time = monotonic()                     # current time
        self.delay_limits = (0.002, 0.2)
        self.vel_limits = (0.0, 10.0)                    # 
        self.vel = 0.0                                   # 
        self.desired_speed = 0.0                         # 
        self.result = 0
        self.wheel_diameter = 0.1263365                  # in m
        self.wheel_radius = self.wheel_diameter / 2      # in m
        # print("Wheel radius: {}".format(wheel_radius))

        self.angle_of_step = 2 * pi / self.SPR                # in radian
        # print("Angle of a step: {}".format(angle_of_step))

        self.distance_of_step = self.wheel_radius * self.angle_of_step     # calc distance per step
        # print("Distance of a step: {}".format(distance_of_step))

        self.right_wheel = PID(kp=0.03, direction=1, output_limits=self.vel_limits, updateTime=0.005)
        # left_wheel = PID(output_limits=vel_limits, updateTime=0.001)
        
        self.timer = self.create_timer(self.result, self.MoveForward)
        self.timer.cancel()
        

    def listener_callback(self, msg : XboxInput):
        self.call_counter += 1
        
        if msg.vel_r >= 1:
            if desired_speed != msg.vel_r:
                self.get_logger().info("Forward motion triggered")
                desired_speed = msg.vel_r
                self.accelerating = True

        elif msg.vel_r <= 1:
            if desired_speed != msg.vel_r:
                self.get_logger().info("Stop motion triggered")
                desired_speed = self.vel_limits[0]
                self.accelarating = False
        
        else:
            desired_speed = self.vel_limits[0]
        
        
        if self.accelerating:
            # control speed
            # vel = right_wheel.compute(desired_speed, self.getCurrentSpeed())
            vel = self.right_wheel.compute(desired_speed, self.current_speed)
            self.current_speed += vel
            self.get_logger().info("New velocity: {}".format(self.current_speed))
            # left_wheel.compute(vel_limits[1], current)
            
            #                       low             high          high             low
            result = self.map(self.current_speed, self.vel_limits[0], self.vel_limits[1], self.delay_limits[1], self.delay_limits[0])
            # print("Result = {}".format(result))
        else:
            vel = 0
            self.current_speed += vel
            #                       low             high          high             low
            result = self.map(self.current_speed, self.vel_limits[0], self.vel_limits[1], self.delay_limits[1], self.delay_limits[0])
            # print("Result = {}".format(result))
        
        if result == self.delay_limits[1]:
            result = 0
            self.timer.cancel()
        else:
            self.timer.reset()
            self.get_logger().info("Resulting delay = {}".format(result))
            self.get_logger().info("Changing time now")
            self.timer.timer_period_ns = result * S_TO_NS
    
    # Mapper, fucking always works
    def map(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)
            
    def getDistance(self):    
        global last_step_count
        # calc step difference
        step_difference = step_count - last_step_count
        self.get_logger().debug("Step difference: {}".format(step_difference))
        
        # calc distance
        distance = self.distance_of_step * step_difference
        self.get_logger().debug("Distance: {}".format(distance))
        
        # save steps
        last_step_count = step_count
        # return distance
        return distance

    def getCurrentSpeed(self):
        # get distance
        distance = self.getDistance()
        # get time
        now = monotonic()
        self.get_logger().debug("Current time: {}".format(now))
        
        global last_time
        # calc time difference
        time_difference = now - last_time
        self.get_logger().debug("Time difference: {}".format(time_difference))
        
        # calc speed
        speed = distance * time_difference
        self.get_logger().debug("Speed: {}".format(speed))
        
        # save time
        last_time = now
        # return speed
        return speed

    def MoveForward(self):
        self.get_logger().info("Stepping now")
        # step both wheels forward once
        GPIO.output(self.StepperRightDIR, self.RFW)
        GPIO.output(self.StepperLeftDIR, self.LFW)
        GPIO.output(self.StepperLeftSTEP, GPIO.HIGH)
        GPIO.output(self.StepperRightSTEP, GPIO.HIGH)
    
        sleep(0.0001)
        # update the counter
        global step_count 
        step_count += 1
        GPIO.output(self.StepperLeftSTEP, GPIO.LOW)
        GPIO.output(self.StepperRightSTEP, GPIO.LOW)


def main(args=None):
    rclpy.init(args=args)

    stepperControl = stepperMotorDriver()

    rclpy.spin(stepperControl)

    stepperControl.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
