from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    xbox_controller = Node(
        package='xbox_input',
        executable='subscriber',
        name='RecievingXboxInput'
    )

    motor_controller = Node(
        package='motor_control',
        executable='stepper_driver2',
        name='MotorController'
    )

    imu_sensor = Node(
        package='imu_sensor',
        executable='publisher',
        name='SendingIMU_data'
    )
    
    tof_sensor = Node(
        package='tof_sensor',
        executable='publisher',
        name='SendingTOF_data'
    )
    
    camera_sensor = Node(
        package='camera',
        executable='publisher',
        name='RecievingIMU_data'
    )
        
    batterystatus_sensor = Node(
        package='battery_status',
        executable='publisher',
        name='SendingBatteryStatus'
    )
    
    ldlidar_node = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        name='LD06',
        output='screen',
        parameters=[
            {'product_name': 'LDLiDAR_LD06'},
            {'topic_name': 'scan'},
            {'port_name': '/dev/ttyS0'},
            {'frame_id': 'base_laser'},
            {'laser_scan_dir': True},
            {'enable_angle_crop_func': False},
            {'angle_crop_min': 135.0},
            {'angle_crop_max': 225.0}
        ]
    )

    # base_link to base_laser tf node
    base_link_to_laser_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_base_laser_ld06',
        arguments=['0','0','0.18','0','0','0','base_link','base_laser']
    )


    # Define LaunchDescription variable
    ld = LaunchDescription()
    
    ld.add_action(xbox_controller)
    ld.add_action(motor_controller)
    ld.add_action(imu_sensor)
    ld.add_action(tof_sensor)
    ld.add_action(camera_sensor)
    ld.add_action(batterystatus_sensor)
    ld.add_action(ldlidar_node)
    ld.add_action(base_link_to_laser_tf_node)
    
    return ld
