[![Build](https://github.com/pierric/parol6-ros2/actions/workflows/docker-image.yml/badge.svg)](https://github.com/pierric/parol6-ros2/actions/workflows/docker-image.yml)

ROS2 package for [PAROL6 Robotic Arm](https://github.com/PCrnjak/PAROL6-Desktop-robot-arm).

![image](https://github.com/pierric/parol6-ros2/assets/141614/3862762b-6193-4e14-beff-bc051c82a7da)

The robotic arm can be control via the ROS topic.
```
ros2 topic pub /joint_trajectory_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory \
  '{joint_names: ["J1", "J2", "J3", "J4", "J5", "J6"], points: [{positions: [0.5,0.5,0.5,0.5,0.5,0.5]}]}' -1
```
