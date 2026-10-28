cmake_minimum_required(VERSION 3.14)
project(wireframe)

set(CMAKE_CXX_STANDARD 20)

# Tell pybind11 to use modern FindPython3
set(PYBIND11_FINDPYTHON ON)

find_package(pybind11 REQUIRED)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)


# build Python extension
pybind11_add_module(wireframe
    wireframe.cpp
    math.cpp
    obj_loader.cpp
)

