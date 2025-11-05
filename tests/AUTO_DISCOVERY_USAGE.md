# Test Auto-Discovery Usage Guide

This guide shows how to use the new test auto-discovery functions to reduce manual test registration in CMakeLists.txt.

## Overview

The auto-discovery functions in `test_discovery.cmake` automatically find and register tests based on file patterns, eliminating the need to manually add each test to CMakeLists.txt.

## Quick Start

### 1. Include the auto-discovery file

Add to your `tests/python/CMakeLists.txt`:

```cmake
# Include auto-discovery functions
include(${CMAKE_SOURCE_DIR}/tests/test_discovery.cmake)
```

### 2. Use auto-discovery instead of manual registration

**Before (manual registration):**
```cmake
add_blender_test(
  bl_pyapi_bpy_path
  --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_bpy_path.py
)
add_blender_test(
  bl_pyapi_bmesh
  --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_bmesh.py
)
add_blender_test(
  bl_pyapi_mathutils
  --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_mathutils.py
)
# ... many more lines ...
```

**After (auto-discovery):**
```cmake
# Auto-discover all Python API tests
add_test_category(
  NAME "pyapi"
  PATTERN "bl_pyapi_*.py"
)
```

## Available Functions

### `add_python_tests_auto()`

Automatically discover and register Python tests matching a pattern.

**Usage:**
```cmake
add_python_tests_auto(
  PATTERN "bl_pyapi_*.py"
  CATEGORY "pyapi"          # Optional: for better logging
  ARGS --verbose            # Optional: extra arguments
)
```

**Example:**
```cmake
# Register all animation tests
add_python_tests_auto(
  PATTERN "bl_animation_*.py"
  CATEGORY "animation"
)
```

### `add_python_tests_with_data_auto()`

Auto-discover tests that require test data.

**Usage:**
```cmake
add_python_tests_with_data_auto(
  PATTERN "bl_io_*.py"
  DATA_DIR "io_tests"
  CATEGORY "io"             # Optional
)
```

**Example:**
```cmake
# Register all I/O tests with test data
add_python_tests_with_data_auto(
  PATTERN "bl_*_io_*.py"
  DATA_DIR "io_tests"
  CATEGORY "io"
)
```

### `add_test_category()`

High-level function that combines pattern matching with optional data.

**Usage:**
```cmake
add_test_category(
  NAME "category_name"
  PATTERN "bl_pattern_*.py"
  WITH_DATA                 # Optional: if tests need data
  DATA_DIR "data_directory" # Required if WITH_DATA is set
  ARGS --verbose            # Optional: extra arguments
)
```

**Examples:**
```cmake
# Simple category without data
add_test_category(
  NAME "pyapi"
  PATTERN "bl_pyapi_*.py"
)

# Category with test data
add_test_category(
  NAME "io"
  PATTERN "bl_*_io_*.py"
  WITH_DATA
  DATA_DIR "io_tests"
)

# Category with extra arguments
add_test_category(
  NAME "blendfile"
  PATTERN "bl_blendfile_*.py"
  ARGS --verbose
)
```

### `add_ui_tests_auto()`

Auto-discover UI simulation tests.

**Usage:**
```cmake
if(WITH_UI_TESTS)
  add_ui_tests_auto(
    PATTERN "test_*.py"
    BASE_DIR "${CMAKE_CURRENT_LIST_DIR}/ui_simulate"
  )
endif()
```

### `add_python_test_functions_auto()`

Advanced: Register individual test functions as separate CTest tests.

**Usage:**
```cmake
add_python_test_functions_auto(
  FILE "bl_complex_test.py"
  PREFIX "complex_"         # Optional: prefix for test names
  ARGS --verbose            # Optional: extra arguments
)
```

This will create separate tests like:
- `complex_bl_complex_test_test_feature1`
- `complex_bl_complex_test_test_feature2`
- etc.

## Migration Guide

### Step 1: Backup your CMakeLists.txt

```bash
cp tests/python/CMakeLists.txt tests/python/CMakeLists.txt.backup
```

### Step 2: Include auto-discovery

Add near the top of `tests/python/CMakeLists.txt`:

```cmake
# Include auto-discovery functions
include(${CMAKE_SOURCE_DIR}/tests/test_discovery.cmake)
```

### Step 3: Replace manual registration sections

Identify groups of similar tests and replace with auto-discovery:

**Example: Python API Tests**

Replace:
```cmake
add_blender_test(bl_pyapi_bpy_path --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_bpy_path.py)
add_blender_test(bl_pyapi_bmesh --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_bmesh.py)
add_blender_test(bl_pyapi_mathutils --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_mathutils.py)
add_blender_test(bl_pyapi_idprop --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_idprop.py)
add_blender_test(bl_pyapi_prop_array --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_prop_array.py)
```

With:
```cmake
add_test_category(NAME "pyapi" PATTERN "bl_pyapi_*.py")
```

**Example: Animation Tests**

Replace:
```cmake
add_blender_test(bl_animation_action --python ${CMAKE_CURRENT_LIST_DIR}/bl_animation_action.py)
add_blender_test(bl_animation_fcurves --python ${CMAKE_CURRENT_LIST_DIR}/bl_animation_fcurves.py)
add_blender_test(bl_animation_bake --python ${CMAKE_CURRENT_LIST_DIR}/bl_animation_bake.py)
```

With:
```cmake
add_test_category(NAME "animation" PATTERN "bl_animation_*.py")
```

### Step 4: Test the changes

```bash
cd build
cmake ..
ctest -N  # List all tests to verify they're registered
ctest     # Run tests to ensure they work
```

### Step 5: Compare test counts

```bash
# Before changes
ctest -N | grep "Test #" | wc -l

# After changes (should be the same)
ctest -N | grep "Test #" | wc -l
```

## Complete Example

Here's a complete example showing how to migrate a section of CMakeLists.txt:

**Before:**
```cmake
# ------------------------------------------------------------------------------
# PYTHON API TESTS
# ------------------------------------------------------------------------------

add_blender_test(bl_pyapi_bpy_path --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_bpy_path.py)
add_blender_test(bl_pyapi_bpy_utils_units --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_bpy_utils_units.py)
add_blender_test(bl_pyapi_bpy_driver_secure_eval --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_bpy_driver_secure_eval.py)
add_blender_test(bl_pyapi_bmesh --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_bmesh.py)
add_blender_test(bl_pyapi_mathutils --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_mathutils.py)
add_blender_test(bl_pyapi_idprop --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_idprop.py)
add_blender_test(bl_pyapi_prop --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_prop.py)
add_blender_test(bl_pyapi_prop_array --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_prop_array.py)
add_blender_test(bl_pyapi_text --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_text.py)
add_blender_test(bl_pyapi_grease_pencil --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_grease_pencil.py)

# ------------------------------------------------------------------------------
# ANIMATION TESTS
# ------------------------------------------------------------------------------

add_blender_test(bl_animation_action --python ${CMAKE_CURRENT_LIST_DIR}/bl_animation_action.py)
add_blender_test(bl_animation_fcurves --python ${CMAKE_CURRENT_LIST_DIR}/bl_animation_fcurves.py)
add_blender_test(bl_animation_bake --python ${CMAKE_CURRENT_LIST_DIR}/bl_animation_bake.py)
add_blender_test(bl_animation_drivers --python ${CMAKE_CURRENT_LIST_DIR}/bl_animation_drivers.py)
add_blender_test(bl_animation_keyframing --python ${CMAKE_CURRENT_LIST_DIR}/bl_animation_keyframing.py)
```

**After:**
```cmake
# Include auto-discovery functions
include(${CMAKE_SOURCE_DIR}/tests/test_discovery.cmake)

# ------------------------------------------------------------------------------
# PYTHON API TESTS
# ------------------------------------------------------------------------------

add_test_category(
  NAME "pyapi"
  PATTERN "bl_pyapi_*.py"
)

# ------------------------------------------------------------------------------
# ANIMATION TESTS
# ------------------------------------------------------------------------------

add_test_category(
  NAME "animation"
  PATTERN "bl_animation_*.py"
)
```

**Lines reduced:** From ~15 lines to ~7 lines (53% reduction)

## Benefits

1. **Less maintenance**: Add new tests by creating files; no CMakeLists.txt changes needed
2. **Consistent naming**: All tests in a category follow the same pattern
3. **Easier to read**: Clear test organization by category
4. **Scalability**: Easy to add many tests at once
5. **Less error-prone**: No risk of forgetting to register a test file

## Excluding Files from Auto-Discovery

Files matching these patterns are automatically excluded:
- `test_*_example.py` - Example files
- `*_template.py` - Template files
- `run*.py` - Runner scripts (for UI tests)
- `*_setup.py` - Setup scripts

To exclude additional files, either:
1. Rename them to match an excluded pattern
2. Keep them but register separately with manual `add_blender_test()`

## Troubleshooting

### Tests not being discovered

**Check:**
1. File name matches the pattern
2. File is not in the excluded patterns
3. Pattern path is correct (relative to CMakeLists.txt)

**Debug:**
```bash
cd build
cmake .. 2>&1 | grep "Auto-discovered"
```

This will show how many tests were found for each pattern.

### Too many tests discovered

Refine the pattern to be more specific:
```cmake
# Too broad
PATTERN "bl_*.py"  # Matches everything starting with bl_

# More specific
PATTERN "bl_pyapi_*.py"  # Only Python API tests
```

### Need to add arguments to specific tests

For tests that need special handling, register them manually:
```cmake
# Auto-discover most tests
add_test_category(NAME "pyapi" PATTERN "bl_pyapi_*.py")

# Manually register special case
add_blender_test(
  bl_pyapi_special
  --python ${CMAKE_CURRENT_LIST_DIR}/bl_pyapi_special.py
  --special-arg value
)
```

## Best Practices

1. **Group by category**: Use consistent prefixes (bl_pyapi_, bl_animation_, etc.)
2. **One category per pattern**: Don't overlap patterns
3. **Document exceptions**: Comment why specific tests are registered manually
4. **Test after changes**: Always run `ctest -N` to verify test count
5. **Keep it simple**: Start with broad categories, refine as needed

## Future Enhancements

Potential improvements to auto-discovery:
- Pytest integration for automatic test function discovery
- Test metadata parsing from docstrings
- Automatic test data detection
- Smart categorization based on imports
- Test dependency detection

---

For questions or issues, see the main [tests/README.md](README.md) or ask on the developer forum.
