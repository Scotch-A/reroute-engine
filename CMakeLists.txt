cmake_minimum_required(VERSION 3.15)
project(reroute_engine CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

add_executable(reroute
    src/main.cpp
    src/data_generator.cpp
    src/solver.cpp
    src/baseline.cpp
)

target_include_directories(reroute PRIVATE src)
