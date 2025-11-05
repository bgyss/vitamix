# SPDX-FileCopyrightText: 2025 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

# Test Auto-Discovery Functions
#
# This file provides CMake functions for automatic test discovery, reducing
# the need for manual test registration in CMakeLists.txt.

# Auto-discover and register Python tests matching a pattern
#
# Usage:
#   add_python_tests_auto(
#     PATTERN "bl_pyapi_*.py"
#     [CATEGORY "pyapi"]
#     [ARGS --verbose]
#   )
#
# This will find all Python files matching the pattern and register them as tests.
function(add_python_tests_auto)
  set(options)
  set(oneValueArgs PATTERN CATEGORY)
  set(multiValueArgs ARGS)
  cmake_parse_arguments(ARG "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  if(NOT ARG_PATTERN)
    message(FATAL_ERROR "add_python_tests_auto: PATTERN argument is required")
  endif()

  # Find all matching test files
  file(GLOB test_files "${CMAKE_CURRENT_LIST_DIR}/${ARG_PATTERN}")

  if(NOT test_files)
    message(STATUS "No tests found matching pattern: ${ARG_PATTERN}")
    return()
  endif()

  set(test_count 0)
  foreach(test_file ${test_files})
    get_filename_component(test_name ${test_file} NAME_WE)

    # Skip example/template files
    if(test_name MATCHES "^test_.*_example" OR test_name MATCHES ".*_template$")
      continue()
    endif()

    # Register the test
    add_blender_test(
      ${test_name}
      --python ${test_file}
      ${ARG_ARGS}
    )

    math(EXPR test_count "${test_count} + 1")
  endforeach()

  if(ARG_CATEGORY)
    message(STATUS "Auto-discovered ${test_count} ${ARG_CATEGORY} tests")
  else()
    message(STATUS "Auto-discovered ${test_count} tests matching ${ARG_PATTERN}")
  endif()
endfunction()

# Auto-discover Python tests with test data
#
# Usage:
#   add_python_tests_with_data_auto(
#     PATTERN "bl_io_*.py"
#     DATA_DIR "io_tests"
#     [CATEGORY "io"]
#   )
function(add_python_tests_with_data_auto)
  set(options)
  set(oneValueArgs PATTERN DATA_DIR CATEGORY)
  set(multiValueArgs)
  cmake_parse_arguments(ARG "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  if(NOT ARG_PATTERN)
    message(FATAL_ERROR "add_python_tests_with_data_auto: PATTERN argument is required")
  endif()
  if(NOT ARG_DATA_DIR)
    message(FATAL_ERROR "add_python_tests_with_data_auto: DATA_DIR argument is required")
  endif()

  # Find all matching test files
  file(GLOB test_files "${CMAKE_CURRENT_LIST_DIR}/${ARG_PATTERN}")

  if(NOT test_files)
    message(STATUS "No tests found matching pattern: ${ARG_PATTERN}")
    return()
  endif()

  set(test_count 0)
  foreach(test_file ${test_files})
    get_filename_component(test_name ${test_file} NAME_WE)

    # Skip example/template files
    if(test_name MATCHES "^test_.*_example" OR test_name MATCHES ".*_template$")
      continue()
    endif()

    # Register the test with data directory
    add_blender_test(
      ${test_name}
      --python ${test_file}
      --
      --testdir ${TEST_SRC_DIR}/${ARG_DATA_DIR}
    )

    math(EXPR test_count "${test_count} + 1")
  endforeach()

  if(ARG_CATEGORY)
    message(STATUS "Auto-discovered ${test_count} ${ARG_CATEGORY} tests with data")
  else()
    message(STATUS "Auto-discovered ${test_count} tests matching ${ARG_PATTERN}")
  endif()
endfunction()

# Auto-discover UI tests
#
# Usage:
#   add_ui_tests_auto(
#     PATTERN "test_*.py"
#     BASE_DIR "${CMAKE_CURRENT_LIST_DIR}/ui_simulate"
#   )
function(add_ui_tests_auto)
  if(NOT WITH_UI_TESTS)
    return()
  endif()

  set(options)
  set(oneValueArgs PATTERN BASE_DIR)
  set(multiValueArgs)
  cmake_parse_arguments(ARG "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  if(NOT ARG_PATTERN)
    message(FATAL_ERROR "add_ui_tests_auto: PATTERN argument is required")
  endif()
  if(NOT ARG_BASE_DIR)
    message(FATAL_ERROR "add_ui_tests_auto: BASE_DIR argument is required")
  endif()

  # Find all matching test files
  file(GLOB test_files "${ARG_BASE_DIR}/${ARG_PATTERN}")

  if(NOT test_files)
    message(STATUS "No UI tests found matching pattern: ${ARG_PATTERN}")
    return()
  endif()

  set(test_count 0)
  foreach(test_file ${test_files})
    get_filename_component(test_name ${test_file} NAME_WE)

    # Skip helper files
    if(test_name MATCHES "^run" OR test_name MATCHES ".*_setup$")
      continue()
    endif()

    # Get test functions from the file
    # This is a simplified version - could be enhanced to parse actual test functions
    set(full_test_name "ui_${test_name}")

    add_blender_test_ui(
      ${full_test_name}
      --python ${ARG_BASE_DIR}/run.py
      --
      --tests ${test_name}
    )

    math(EXPR test_count "${test_count} + 1")
  endforeach()

  message(STATUS "Auto-discovered ${test_count} UI tests")
endfunction()

# Discover tests by parsing Python file for test functions
#
# This is more sophisticated - it actually parses the Python file to find test functions
# Usage:
#   add_python_test_functions_auto(
#     FILE "bl_complex_test.py"
#     [PREFIX "complex_"]
#   )
#
# This will create separate tests for each test function found in the file
function(add_python_test_functions_auto)
  set(options)
  set(oneValueArgs FILE PREFIX)
  set(multiValueArgs ARGS)
  cmake_parse_arguments(ARG "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  if(NOT ARG_FILE)
    message(FATAL_ERROR "add_python_test_functions_auto: FILE argument is required")
  endif()

  set(test_file "${CMAKE_CURRENT_LIST_DIR}/${ARG_FILE}")
  if(NOT EXISTS ${test_file})
    message(WARNING "Test file not found: ${test_file}")
    return()
  endif()

  get_filename_component(test_basename ${test_file} NAME_WE)

  # Read the file to find test functions
  file(READ ${test_file} file_contents)

  # Find all test methods (simplified regex - could be enhanced)
  string(REGEX MATCHALL "def (test_[a-zA-Z0-9_]+)\\(" test_functions "${file_contents}")

  set(test_count 0)
  foreach(test_match ${test_functions})
    # Extract function name from "def test_name("
    string(REGEX REPLACE "def ([a-zA-Z0-9_]+)\\(" "\\1" func_name "${test_match}")

    # Create unique test name
    if(ARG_PREFIX)
      set(full_test_name "${ARG_PREFIX}${test_basename}_${func_name}")
    else()
      set(full_test_name "${test_basename}_${func_name}")
    endif()

    # Register individual test function
    add_blender_test(
      ${full_test_name}
      --python ${test_file}
      ${ARG_ARGS}
      --
      ${func_name}
    )

    math(EXPR test_count "${test_count} + 1")
  endforeach()

  if(test_count GREATER 0)
    message(STATUS "Auto-discovered ${test_count} test functions in ${ARG_FILE}")
  endif()
endfunction()

# Batch register tests from a category
#
# Usage:
#   add_test_category(
#     NAME "pyapi"
#     PATTERN "bl_pyapi_*.py"
#     [WITH_DATA]
#     [DATA_DIR "pyapi_tests"]
#   )
function(add_test_category)
  set(options WITH_DATA)
  set(oneValueArgs NAME PATTERN DATA_DIR)
  set(multiValueArgs ARGS)
  cmake_parse_arguments(ARG "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  if(NOT ARG_NAME)
    message(FATAL_ERROR "add_test_category: NAME argument is required")
  endif()
  if(NOT ARG_PATTERN)
    message(FATAL_ERROR "add_test_category: PATTERN argument is required")
  endif()

  if(ARG_WITH_DATA)
    if(NOT ARG_DATA_DIR)
      message(FATAL_ERROR "add_test_category: DATA_DIR required when WITH_DATA is set")
    endif()
    add_python_tests_with_data_auto(
      PATTERN ${ARG_PATTERN}
      DATA_DIR ${ARG_DATA_DIR}
      CATEGORY ${ARG_NAME}
    )
  else()
    add_python_tests_auto(
      PATTERN ${ARG_PATTERN}
      CATEGORY ${ARG_NAME}
      ARGS ${ARG_ARGS}
    )
  endif()
endfunction()

# Example usage (commented out):
#
# # Auto-discover all Python API tests
# add_test_category(
#   NAME "pyapi"
#   PATTERN "bl_pyapi_*.py"
# )
#
# # Auto-discover all I/O tests with test data
# add_test_category(
#   NAME "io"
#   PATTERN "bl_*_io_*.py"
#   WITH_DATA
#   DATA_DIR "io_tests"
# )
#
# # Auto-discover animation tests
# add_test_category(
#   NAME "animation"
#   PATTERN "bl_animation_*.py"
# )
