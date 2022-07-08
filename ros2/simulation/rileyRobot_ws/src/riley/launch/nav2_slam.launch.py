import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Configuration Paths
    nav2_configs = os.path.join(get_package_share_directory('riley'), 'config', 'nav2')
    slam_config = os.path.join(get_package_share_directory('riley'), 'config', 'slam', 'localization.yaml')
    nav2_bt_trees = os.path.join(get_package_share_directory("nav2_bt_navigator"), "behavior_trees")

    # Node Lifecycle Order
    lifecycle_managed_nodes = ['controller_server','planner_server','recoveries_server', 'bt_navigator','waypoint_follower']

    # Parameters Setup
    map_slam_file = LaunchConfiguration('map')
    map_slam_file_arg = DeclareLaunchArgument('map', description='Absolute path to the slam-toolbox map files')
    map_slam_pose = LaunchConfiguration('map_pose')
    map_slam_pose_arg = DeclareLaunchArgument('map_pose', description='Pose array for localisation start')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='True', description="Use Simulation clock?")

    # Nodes
    slam_node = Node(
        parameters=[
            slam_config,
            {'use_sim_time': use_sim_time},
            {'map_file_name': map_slam_file},
            {'map_start_pose': map_slam_pose}
        ],
        package='slam_toolbox',
        executable='localization_slam_toolbox_node',
        name='slam_toolbox',
        output='screen')
    nav_group = GroupAction([
        Node(
            package='nav2_controller',
            executable='controller_server',
            output='screen',
            parameters=[
                nav2_configs + "/controller_dwb.yaml",
                {"use_sim_time": use_sim_time}]),
        
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[
                nav2_configs + "/planner.yaml",
                {"use_sim_time": use_sim_time}]),

        Node(
            package='nav2_recoveries',
            executable='recoveries_server',
            name='recoveries_server',
            output='screen',
            parameters=[
                nav2_configs + "/recoveries.yaml",
                {"use_sim_time": use_sim_time}]),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[
                nav2_configs + "/bt_navigator.yaml",
                {"use_sim_time": use_sim_time},
                {"default_bt_xml_filename" : nav2_bt_trees + "/navigate_w_replanning_and_recovery.xml"}
            ]),

        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[
                nav2_configs + "/waypoint.yaml",
                {"use_sim_time": use_sim_time}])  
    ])
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'autostart': True},
            {'node_names': lifecycle_managed_nodes}])

    # Return setup
    ld = LaunchDescription()
    ld.add_action(map_slam_file_arg)
    ld.add_action(map_slam_pose_arg)
    ld.add_action(use_sim_time_arg)
    ld.add_action(slam_node)
    ld.add_action(nav_group)
    ld.add_action(lifecycle_manager)

    return ld
