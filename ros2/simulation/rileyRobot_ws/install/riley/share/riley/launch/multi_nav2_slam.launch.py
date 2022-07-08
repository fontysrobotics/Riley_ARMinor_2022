import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, TextSubstitution
from nav2_common.launch import RewrittenYaml

def generate_launch_description():
    # Configuration Paths
    nav2_configs = os.path.join(get_package_share_directory('riley'), 'config', 'nav2')
    slam_config = os.path.join(get_package_share_directory('riley'), 'config', 'slam')
    nav2_bt_trees = os.path.join(get_package_share_directory("nav2_bt_navigator"), "behavior_trees")

    # Node Lifecycle Order
    lifecycle_names_base = ['controller_server','planner_server','recoveries_server', 'bt_navigator','waypoint_follower']

    # Parameters Setup
    map_slam_file = LaunchConfiguration('map')
    map_slam_file_arg = DeclareLaunchArgument('map', description='Absolute path to the slam-toolbox map files')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='True', description="Use Simulation clock?")

    # Remap
    remappings_tf = [
        ('/tf', 'tf'),
        ('/tf_static', 'tf_static')]
    remappings_map = [
        ('/tf', 'tf'),
        ('/tf_static', 'tf_static'),
        ('/initialpose', 'initialpose'),
        ('/slam_toolbox/graph_visualization', 'slam_toolbox/graph_visualization'),
        ('/slam_toolbox/scan_visualization', 'slam_toolbox/scan_visualization')]

    # Define robots
    robot_define = [
        {"name" : "dede1",
        "robot_pose" : [4.0, 3.0, 0.1],
        "slam": "localization.yaml",
        "controller": "controller_dwb.yaml",
        "planner": "planner.yaml",
        "recoveries" : "recoveries.yaml",
        "bt_navigator_config": "bt_navigator.yaml", 
        "bt_navigator_tree": "navigate_w_replanning_and_recovery.xml",
        "waypoint_follower" : "waypoint.yaml"},
        {"name" : "dede2",
        "robot_pose" : [7.0, 3.0, 0.1],
        "slam": "localization.yaml",
        "controller": "controller_dwb.yaml",
        "planner": "planner.yaml",
        "recoveries" : "recoveries.yaml",
        "bt_navigator_config": "bt_navigator.yaml", 
        "bt_navigator_tree": "navigate_w_replanning_and_recovery.xml",
        "waypoint_follower" : "waypoint.yaml"}
    ]

    # Spawn Navigation
    navigation_group = []
    lifecycle_names_target = []
    for robot in robot_define:
        param_remap_costmap ={
            "map_topic": "/" + robot["name"] + "/map",
            "topic" : "/" + robot["name"] + "/scan",
            "use_sim_time": use_sim_time
        }
        slam_item = Node(
            package='slam_toolbox',
            executable='localization_slam_toolbox_node',
            namespace=TextSubstitution(text=robot["name"]),
            name='slam_toolbox',
            remappings=remappings_map,
            output='screen',
            parameters=[
                RewrittenYaml(
                    source_file=TextSubstitution(text=(slam_config + "/" + robot["slam"])),
                    root_key=TextSubstitution(text=robot["name"]),
                    param_rewrites={},
                    convert_types=True),
                {'use_sim_time': use_sim_time},
                {'map_file_name': map_slam_file},
                {'map_start_pose': robot["robot_pose"]}
        ])
        group_item = GroupAction([
            Node(
                package='nav2_controller',
                executable='controller_server',
                output='screen',
                namespace=TextSubstitution(text=robot["name"]),
                remappings=remappings_tf,
                parameters=[
                    RewrittenYaml(
                        source_file=TextSubstitution(text=(nav2_configs + "/" + robot["controller"])),
                        root_key=TextSubstitution(text=robot["name"]),
                        param_rewrites=param_remap_costmap,
                        convert_types=True),
                    {"use_sim_time": use_sim_time}]),
        
            Node(
                package='nav2_planner',
                executable='planner_server',
                name='planner_server',
                output='screen',
                namespace=TextSubstitution(text=robot["name"]),
                remappings=remappings_tf,
                parameters=[
                    RewrittenYaml(
                        source_file=TextSubstitution(text=(nav2_configs + "/" + robot["planner"])),
                        root_key=TextSubstitution(text=robot["name"]),
                        param_rewrites=param_remap_costmap,
                        convert_types=True),
                    {"use_sim_time": use_sim_time}]),

            Node(
                package='nav2_recoveries',
                executable='recoveries_server',
                name='recoveries_server',
                output='screen',
                namespace=TextSubstitution(text=robot["name"]),
                remappings=remappings_tf,
                parameters=[
                    RewrittenYaml(
                        source_file=TextSubstitution(text=(nav2_configs + "/" + robot["recoveries"])),
                        root_key=TextSubstitution(text=robot["name"]),
                        param_rewrites={},
                        convert_types=True),
                    {"use_sim_time": use_sim_time}]),

            Node(
                package='nav2_bt_navigator',
                executable='bt_navigator',
                name='bt_navigator',
                output='screen',
                namespace=TextSubstitution(text=robot["name"]),
                remappings=remappings_tf,
                parameters=[
                    RewrittenYaml(
                        source_file=TextSubstitution(text=(nav2_configs + "/" + robot["bt_navigator_config"])),
                        root_key=TextSubstitution(text=robot["name"]),
                        param_rewrites={},
                        convert_types=True),
                    {"use_sim_time": use_sim_time},
                    {"default_bt_xml_filename" : nav2_bt_trees + "/" + robot["bt_navigator_tree"]}
                ]),

            Node(
                package='nav2_waypoint_follower',
                executable='waypoint_follower',
                name='waypoint_follower',
                output='screen',
                namespace=TextSubstitution(text=robot["name"]),
                remappings=remappings_tf,
                parameters=[
                    RewrittenYaml(
                        source_file=TextSubstitution(text=(nav2_configs + "/" + robot["waypoint_follower"])),
                        root_key=TextSubstitution(text=robot["name"]),
                        param_rewrites={},
                        convert_types=True),
                    {"use_sim_time": use_sim_time}])
        ])
        navigation_group.append(slam_item)
        navigation_group.append(group_item)
        for item in lifecycle_names_base:
            lifecycle_names_target.append(robot["name"] + "/" + item)

    # Lifecycle manager
    lifecycle_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'autostart': True},
            {'node_names': lifecycle_names_target}])

    # Launch Description Setup
    ld = LaunchDescription()
    ld.add_action(map_slam_file_arg)
    ld.add_action(use_sim_time_arg)
    for item in navigation_group:
        ld.add_action(item)
    ld.add_action(lifecycle_node)
    return ld
