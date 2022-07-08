import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Paramater Setup
    rviz_namespace = LaunchConfiguration('namespace')
    rviz_namespace_arg = DeclareLaunchArgument('namespace', description='Namespace for Rviz2')
    
    # Rviz2 remap
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        namespace='rviz2',
        output='screen',
        remappings=[('/tf', 'tf'),
                    ('/tf_static', 'tf_static'),
                    ('/goal_pose', 'goal_pose'),
                    ('/clicked_point', 'clicked_point'),
                    ('/initialpose', 'initialpose')]
    )

    # Launch Description Setup
    ld = LaunchDescription()
    ld.add_action(rviz_namespace_arg)
    ld.add_action(rviz_node)
    return ld
