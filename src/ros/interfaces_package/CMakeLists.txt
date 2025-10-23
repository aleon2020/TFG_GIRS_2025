cmake_minimum_required(VERSION 3.8)
project(interfaces_package)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)

# find_package(sensor_msgs REQUIRED)
# find_package(tf2_ros REQUIRED)
# find_package(tf2_geometry_msgs REQUIRED)

set(ROSIDL_GENERATE_TYPE_DESCRIPTION OFF)

rosidl_generate_interfaces(${PROJECT_NAME}
  # "action/CountUntil.action"
  "msg/EffectorCoordinates.msg"
  "msg/CableParameters.msg"
  "msg/PulleyParameters.msg"
  "msg/EffectorPath.msg"
  "msg/EffectorPosition.msg"
  DEPENDENCIES geometry_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_export_dependencies(geometry_msgs)

ament_package()