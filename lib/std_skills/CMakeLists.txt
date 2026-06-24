# Copyright (c) 2024 PAL Robotics S.L. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cmake_minimum_required(VERSION 3.8)
project(std_skills)

find_package(ament_cmake_auto REQUIRED)
find_package(rosidl_default_generators REQUIRED)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wno-float-equal)
endif()

set(msg_files
    "msg/Bool.msg"
    "msg/Byte.msg"
    "msg/Char.msg"
    "msg/ColorRGBA.msg"
    "msg/Empty.msg"
    "msg/Feedback.msg"
    "msg/Float32Array.msg"
    "msg/Float32.msg"
    "msg/Float64.msg"
    "msg/Int16Array.msg"
    "msg/Int16.msg"
    "msg/Int32Array.msg"
    "msg/Int32.msg"
    "msg/Int64.msg"
    "msg/Int8Array.msg"
    "msg/Int8.msg"
    "msg/Meta.msg"
    "msg/Result.msg"
    "msg/StringArray.msg"
    "msg/String.msg"
    "msg/UInt16Array.msg"
    "msg/UInt16.msg"
    "msg/UInt32Array.msg"
    "msg/UInt32.msg"
    "msg/UInt64.msg"
    "msg/UInt8Array.msg"
    "msg/UInt8.msg"
)

set(srv_files
    "srv/Empty.srv"
    "srv/SetBool.srv"
    "srv/SetFloat32Array.srv"
    "srv/SetFloat32.srv"
    "srv/SetInt8Array.srv"
    "srv/SetInt8.srv"
    "srv/SetStringArray.srv"
    "srv/SetString.srv"
    "srv/SetUInt8Array.srv"
    "srv/SetUInt8.srv"
    "srv/Trigger.srv"
)

set(action_files
    "action/Empty.action"
)

rosidl_generate_interfaces(${PROJECT_NAME}
    ${msg_files}
    ${srv_files}
    ${action_files}
    DEPENDENCIES
        action_msgs
    ADD_LINTER_TESTS
)

ament_export_dependencies(rosidl_default_runtime)

if(BUILD_TESTING)
  ament_auto_find_test_dependencies()
  ament_lint_auto_find_test_dependencies()
endif()

ament_auto_package()
