import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    world = os.path.join(get_package_share_directory('riley'), 'worlds', "my_world.sdf")
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    robot_urdf = os.path.join(get_package_share_directory('riley'), 'Riley_URDF', "riley_robot.urdf")
    
    gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource( os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': world, "verbose": 'true'}.items()
    )

    gz_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py'))
    )

    robot_state = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[robot_urdf]
    )

    ld = LaunchDescription()
    ld.add_action(gz_server)
    ld.add_action(gz_client)
    ld.add_action(robot_state)
    return ld
