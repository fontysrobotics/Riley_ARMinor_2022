#!/usr/bin/env python3
import argparse
import rclpy
from rclpy.node import Node
from xbox_input.XboxController import XboxController
from riley_interfaces.msg import XboxInput

# Maximum allowed wheel velocity (regular and spin movement)
MAX_WHEEL_VEL = 10
MAX_WHEEL_VEL_SPIN = MAX_WHEEL_VEL / 2

# Thresholds to consider joystick input either neutral (min) or fully tilted (max)
XBOX_JOYSTICK_MIN_THRESHOLD = 0.1
XBOX_JOYSTICK_MAX_THRESHOLD = 0.999

xbox = XboxController()
xbox.InvertJoyYAxis = True

class XboxInputPublisher(Node):
    
    def XboxJoystickToWheelVel(self):
        # Init wheel velocities
        crt_vel_lw = 0
        crt_vel_rw = 0

        joy_x, joy_y, _ = xbox.read()

        # Filter joystick inputs using the threshods
        if abs(joy_x) < XBOX_JOYSTICK_MIN_THRESHOLD:
            filter_joy_x = 0
        elif abs(joy_x) > XBOX_JOYSTICK_MAX_THRESHOLD:
            filter_joy_x = round(joy_x)
        else:
            filter_joy_x = joy_x
        if abs(joy_y) < XBOX_JOYSTICK_MIN_THRESHOLD:
            filter_joy_y = round(joy_y)
        elif abs(joy_y) > XBOX_JOYSTICK_MAX_THRESHOLD:
            filter_joy_y = round(joy_y)
        else:
            filter_joy_y = joy_y
        
        # Translate X axis into spin velocity when Y axis reads neutral
        if filter_joy_y == 0 and filter_joy_x != 0:
            crt_vel_lw = filter_joy_x * MAX_WHEEL_VEL_SPIN
            crt_vel_rw = -filter_joy_x * MAX_WHEEL_VEL_SPIN
        else: # Translate Y axis into forward/backward velocity
            crt_vel_lw = filter_joy_y * MAX_WHEEL_VEL
            crt_vel_rw = filter_joy_y * MAX_WHEEL_VEL

        # Then translate X axis into differential wheel velocity proportionally
        if filter_joy_x > 0 and filter_joy_y != 0:
            crt_vel_rw -= filter_joy_x * crt_vel_rw
        elif filter_joy_x < 0 and filter_joy_y != 0:
            crt_vel_lw += filter_joy_x * crt_vel_lw

        #print('X: ', filter_joy_x, ', Y: ', filter_joy_y, ', LW: ', crt_vel_lw, ', RW: ', crt_vel_rw)
        return [float(crt_vel_lw), float(crt_vel_rw)]

    def XboxStartToMotorToggle(self): # Signal to turn motors on/off
        start_btn = xbox.read()[2]
        if start_btn == 1 and self.motor_state_changed == False:
            if self.motor_state == False:
                self.motor_state = True
            else:
                self.motor_state = False
            self.motor_state_changed = True
        elif start_btn == 0:
            self.motor_state_changed = False
        return self.motor_state

    
    def __init__(self, robot_id = 0):
        self.robot_id = robot_id # Store robot ID (used to control a specific robot on the network)
        # Motors should init as turned off
        self.motor_state_changed : bool = False
        self.motor_state : bool = False

        super().__init__('xbox_input_publisher')
        self.publisher = self.create_publisher(XboxInput, 'xbox_input', 10)
        timer_period = 0.05  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = XboxInput()
        msg.vel_l, msg.vel_r = self.XboxJoystickToWheelVel()
        msg.motor_state = self.XboxStartToMotorToggle()
        msg.robot_id = self.robot_id
        self.publisher.publish(msg)
        self.get_logger().info('Publishing: vel_l: %f, vel_r: %f, motor_state: %d, robot_id: %d' % (msg.vel_l, msg.vel_r, msg.motor_state, msg.robot_id))


def main(args=None):
    # Parse arguments for a specific robot_id, otherwise default it to 0
    # Commented because it creates an error in the RILey launch file
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--robot_id', type=int, help='robot ID needed to control a specific robot on the network')
    # args = parser.parse_args()
    # args.robot_id = int(0 if args.robot_id is None else args.robot_id)

    rclpy.init(args=None)

    xbox_publisher = XboxInputPublisher(0)#(args.robot_id)

    rclpy.spin(xbox_publisher)

    xbox_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()