from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import LaunchConfigurationEquals
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Packages
    pkg_clearpath_control = FindPackageShare('clearpath_control')

    # Launch Configurations
    config_localization = LaunchConfiguration('localization_config')
    platform_model = LaunchConfiguration('platform_model')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Launch Arguments
    arg_platform_model = DeclareLaunchArgument(
        'platform_model',
        choices=['a200', 'j100'],
        default_value='a200'
    )

    arg_localization_config = DeclareLaunchArgument(
        'localization_config',
        default_value=PathJoinSubstitution([
          pkg_clearpath_control, 'config', platform_model, 'localization.yaml'])
    )

    arg_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        choices=['true', 'false'],
        default_value='false',
        description='Use simulation time'
    )

    # Localization
    node_localization = Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_node',
            output='screen',
            parameters=[
                config_localization,
                {'use_sim_time', use_sim_time}],
            remappings=[
              ('odometry/filtered', 'platform/odom/filtered'),
            ]
        )

    ld = LaunchDescription()
    ld.add_action(arg_platform_model)
    ld.add_action(arg_localization_config)
    ld.add_action(arg_use_sim_time)
    ld.add_action(node_localization)
    return ld
