cmake_minimum_required(VERSION 3.30)
project(TotalPear_reader)

set(CMAKE_CXX_STANDARD 23)

add_library(${PROJECT_NAME} SHARED
        reader.cpp reader.h
)

target_include_directories(${PROJECT_NAME} PRIVATE "libs/json/include")
