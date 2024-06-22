FROM osrf/ros:jazzy-simulation
RUN apt-get update && apt-get install -y xvfb
WORKDIR /ws
ADD . src/parol6
RUN rosdep install -y --from-paths src
RUN . /opt/ros/jazzy/setup.sh && colcon build
ENTRYPOINT ["/ws/src/parol6/script/entrypoint"]
