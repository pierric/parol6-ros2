from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    ExecuteProcess,
    RegisterEventHandler,
    GroupAction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    declared_arguments = [
        DeclareLaunchArgument(
            "rviz_only",
            default_value="true",
            description="Start Rviz2 with Joint State Publisher gui.",
        ),
        #DeclareLaunchArgument(
        #    "rviz_skip",
        #    default_value="false",
        #    description="Don't run Rivz2",
        #),
    ]
    rviz_only = LaunchConfiguration("rviz_only")
    rviz_skip = LaunchConfiguration("rviz_skip")
    # krviz_skip = False

    pkg_ros_gz_sim = Path(get_package_share_directory("ros_gz_sim"))
    pkg_parol6 = Path(get_package_share_directory("parol6"))

    robot_description_file = pkg_parol6 / "urdf" / "PAROL6.urdf"
    robot_description_config = xacro.process_file(str(robot_description_file))

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[
            {"use_sim_time": True},
            {"robot_description": robot_description_config.toxml()},
        ],
    )

    world = pkg_parol6 / "urdf" / "world.sdf"
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(pkg_ros_gz_sim / "launch" / "gz_sim.launch.py")),
        launch_arguments={"gz_args": f" -r -v 4 {world}"}.items(),
    )

    spawn_model = Node(
        package="ros_gz_sim",
        executable="create",
        parameters=[
            {
                "world": "empty",
                "name": "parol6",
                "topic": "robot_description",
                "allow_renaming": True,
                "z": 0.0,
            }
        ],
        output="screen",
    )

    # bridge = Node(
    #     package="ros_gz_bridge",
    #     executable="parameter_bridge",
    #     arguments=[
    #         "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
    #         "/world/empty/model/parol6/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model",
    #     ],
    #     remappings=[
    #         ("/world/empty/model/parol6/joint_state", "joint_states"),
    #     ],
    #     output="screen",
    # )

    # not possible via Node. It won't discover the /controller_manager
    #
    # joint_state_broadcaster = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    # )
    #
    # joint_controller = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["position_controller", "--controller-manager", "/controller_manager"],
    # )

    joint_state_broadcaster = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'joint_state_broadcaster'],
        output='screen'
    )

    joint_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'joint_trajectory_controller'],
        output='screen'
    )

    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        condition=IfCondition(rviz_only),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", str(pkg_parol6 / "config" / "joint_states.rviz")],
        condition=UnlessCondition(rviz_skip),
    )

    return LaunchDescription(
        [
            *declared_arguments,
            GroupAction(
                [
                    gazebo,
                    spawn_model,
                    RegisterEventHandler(
                        event_handler=OnProcessExit(
                            target_action=spawn_model,
                            on_exit=[joint_state_broadcaster],
                        )
                    ),
                    RegisterEventHandler(
                        event_handler=OnProcessExit(
                            target_action=spawn_model,
                            on_exit=[joint_controller],
                        )
                    ),
                    # bridge,
                ],
                condition=UnlessCondition(rviz_only),
            ),
            robot_state_publisher,
            joint_state_publisher_gui_node,
            rviz,
        ]
    )
