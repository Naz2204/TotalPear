cmake_minimum_required(VERSION 3.30)
project(TotalPear)

set(CMAKE_CXX_STANDARD 23)

add_executable(${PROJECT_NAME}
        main.cpp
        reader.cpp reader.h
        stack.cpp stack.h
        executor.cpp
        executor.h
)

target_include_directories(${PROJECT_NAME} PRIVATE "libs/json/include")

# copy to build
add_custom_command(
        TARGET  ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_LIST_DIR}/data/test.postfix ${CMAKE_BINARY_DIR}
        COMMENT "Copying data file"
)