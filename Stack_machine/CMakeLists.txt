cmake_minimum_required(VERSION 3.30)
project(TotalPear)

set(CMAKE_CXX_STANDARD 23)

# -----
# .dll - reader
add_subdirectory(reader_lib)

# -----

add_executable(${PROJECT_NAME}
        main.cpp
#        reader.cpp reader.h
        stack.cpp stack.h
        executor.cpp
        executor.h
)

target_link_libraries(${PROJECT_NAME} PRIVATE TotalPear_reader)

#target_include_directories(${PROJECT_NAME} PRIVATE "libs/json/include")

# copy .dll
add_custom_command(
        TARGET  ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_BINARY_DIR}/reader_lib/libTotalPear_reader.dll ${CMAKE_CURRENT_BINARY_DIR}
        DEPENDS TotalPear_reader
        COMMENT "Copying reader library"
)

# copy to build
add_custom_command(
        TARGET  ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_LIST_DIR}/data/test.postfix ${CMAKE_BINARY_DIR}
        COMMENT "Copying data file"
)