from launch import LaunchDescription
from launch_ros.actions import Node
import launch_ros
import os
import launch
from launch.substitutions import Command, LaunchConfiguration

def generate_launch_description():
    pkg_share = launch_ros.substitutions.FindPackageShare(package='my_riley_robot_description').find('my_riley_robot_description')
    default_model_path = os.path.join(pkg_share, 'Riley_URDF/riley_robot.urdf.xacro')
    default_rviz_config_path = os.path.join(pkg_share, 'rviz/rileyLidar.rviz')
    #world_path=os.path.join(pkg_share, 'worlds/my_world.sdf')
    
    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}]
    )
    joint_state_publisher_node = launch_ros.actions.Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
        
    )
    rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )
    
    spawn_entity = launch_ros.actions.Node(
    	package='gazebo_ros', 
    	executable='spawn_entity.py',
        arguments=['-entity', 'riley_robot', '-topic', 'robot_description'],
        output='screen'
    )
    robot_localization_node = launch_ros.actions.Node(
         package='robot_localization',
         executable='ekf_node',
         name='ekf_filter_node',
         output='screen',
         parameters=[os.path.join(pkg_share, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )




    xbox_controller = Node(
        package='xbox_input',
        executable='publisher',
        name='SendingXboxInput'
    )

    imu_sensor = Node(
        package='imu_sensor',
        executable='subscriber',
        name='RecievingIMU_data'
    )

    tof_sensor = Node(
        package='tof_sensor',
        executable='subscriber',
        name='RecievingTOF_data'
    )

    camera_sensor = Node(
        package='camera',
        executable='subscriber',
        name='RecievingCameraFeed'
    )

    batterystatus_sensor = Node(
        package='battery_status',
        executable='subscriber',
        name='RecievingBatteryStatus'
    )



    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument(name='model', default_value=default_model_path,
                                            description='Absolute path to robot urdf file'),
        launch.actions.DeclareLaunchArgument(name='rvizconfig', default_value=default_rviz_config_path,
                                            description='Absolute path to rviz config file'),
        launch.actions.DeclareLaunchArgument(name='use_sim_time', default_value='True',
                                            description='Flag to enable use_sim_time'),
        #launch.actions.ExecuteProcess(cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', world_path], output='screen'),
        joint_state_publisher_node,
        robot_state_publisher_node,
        spawn_entity,
        robot_localization_node,
        rviz_node,
        xbox_controller,
        imu_sensor,
        tof_sensor,
        camera_sensor,
        batterystatus_sensor
    ])
