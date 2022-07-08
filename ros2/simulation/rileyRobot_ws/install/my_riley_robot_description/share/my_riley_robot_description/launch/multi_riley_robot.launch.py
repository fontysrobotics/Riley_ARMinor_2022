#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os

from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, TextSubstitution



def gen_robot_list(number_of_robots):

    robots = []

    for i in range(number_of_robots):
        robot_name = "riley_robot"+str(i)
        x_pos = float(i)
        robots.append({'name': robot_name, 'x_pose': x_pos, 'y_pose': 0.0, 'z_pose': 0.01})


    return robots 

def generate_launch_description():

    urdf = os.path.join(get_package_share_directory('my_riley_robot_description'), 'Riley_URDF/', 'riley_robot.urdf')
    pkg_my_riley_robot_description = get_package_share_directory('my_riley_robot_description')
    #assert os.path.exists(urdf), "Theriley_robot.urdf doesnt exist in "+str(urdf)

    # Names and poses of the robots
    robots = gen_robot_list(5)

    # We create the list of spawn robots commands
    spawn_robots_cmds = []

    print(str(robots))
    for robot in robots:
        #print("#############"+str(robot))
        spawn_robots_cmds.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(pkg_my_riley_robot_description, 'launch',
                                                           'spawn_riley_robot_launch.py')),
                launch_arguments={
                                  'robot_urdf': urdf,
                                  'x': TextSubstitution(text=str(robot['x_pose'])),
                                  'y': TextSubstitution(text=str(robot['y_pose'])),
                                  'z': TextSubstitution(text=str(robot['z_pose'])),
                                  'robot_name': robot['name'],
                                  'robot_namespace': robot['name']
                                  }.items()))

    # Create the launch description and populate
    ld = LaunchDescription()
    
    for spawn_robot_cmd in spawn_robots_cmds:
        ld.add_action(spawn_robot_cmd)

    return ld
