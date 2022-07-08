import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node

def generate_launch_description():
    # Configuration paths
    mapping_config_file = os.path.join(get_package_share_directory('riley'), 'config', 'slam', 'mapping.yaml')

    # Parameters setup
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true', description="Use Gazebo time")
    use_map_resume = LaunchConfiguration('use_map_file')
    use_map_resume_arg = DeclareLaunchArgument('use_map_file', default_value='False', description="Resume from existing map?")
    param_map_path = LaunchConfiguration('map_file')
    param_map_path_arg = DeclareLaunchArgument('map_file', default_value='', description="Map file path for continuation")
    param_map_pose = LaunchConfiguration('map_pose')
    param_map_pose_arg = DeclareLaunchArgument('map_pose', default_value="[0.0, 0.0, 0.0]", description="Map start pose")

    # Nodes and flow control
    slam_node_default = GroupAction([ 
        Node(
            parameters=[
                mapping_config_file,
                {'use_sim_time': use_sim_time},
            ],
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen')
        ],
        condition=IfCondition(PythonExpression(['not ', use_map_resume])),
        scoped=False)

    slam_node_resume = GroupAction([
        Node(
            parameters=[
                mapping_config_file,
                {'use_sim_time': use_sim_time},
                {'map_file_name': param_map_path},
                {'map_start_pose': param_map_pose}
            ],
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen')
        ],
        condition=IfCondition(use_map_resume),
        scoped=False)

    # Return object
    ld = LaunchDescription()
    ld.add_action(use_map_resume_arg)
    ld.add_action(param_map_pose_arg)
    ld.add_action(param_map_path_arg)
    ld.add_action(use_sim_time_arg)
    ld.add_action(slam_node_default)
    ld.add_action(slam_node_resume)
    
    return ld
