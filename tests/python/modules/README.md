# Test Utilities Module

This directory contains shared utilities and helper modules for Blender's Python test suite.

## Overview

The test utilities provide common functionality used across multiple test files, including:
- Render testing and image comparison
- I/O testing and validation
- Mesh validation and comparison
- Test reporting and output formatting
- Test markers for categorization

## Available Modules

### Core Testing Utilities

#### `test_utils.py`

General-purpose test utilities for running Blender tests.

**Key Classes:**
- `AbstractBlenderRunnerTest` - Base class for tests that need to run Blender subprocess

**Key Functions:**
- `with_tempdir(func)` - Decorator that provides a temporary directory for test functions

**Usage:**
```python
from modules.test_utils import AbstractBlenderRunnerTest, with_tempdir

class MyTest(AbstractBlenderRunnerTest):
    blender = pathlib.Path("/path/to/blender")
    testdir = pathlib.Path("/path/to/test/files")

    def test_something(self):
        output = self.run_blender("test.blend", "import bpy; print(bpy.app.version)")
        self.assertIn("version", output)

@with_tempdir
def test_with_temp_directory(tempdir):
    # tempdir is a pathlib.Path to a temporary directory
    test_file = tempdir / "test.txt"
    test_file.write_text("test data")
    # Directory is automatically cleaned up after function returns
```

---

#### `mesh_test.py`

Comprehensive framework for testing mesh modifiers and operators.

**Key Classes:**

1. **`ModifierSpec`** - Specifies a modifier to apply
   ```python
   ModifierSpec("myModifier", "SUBSURF", {"levels": 2, "render_levels": 2})
   ```

2. **`OperatorSpecEditMode`** - Specifies an edit mode operator
   ```python
   OperatorSpecEditMode("bevel", {"offset": 0.1}, "EDGE", [1, 2, 3])
   ```

3. **`OperatorSpecObjectMode`** - Specifies an object mode operator
   ```python
   OperatorSpecObjectMode("shade_smooth", {})
   ```

4. **`MeshTest`** - Abstract base class for mesh testing
   - Automatically duplicates objects for testing
   - Compares results with expected objects
   - Supports auto-update of reference objects

5. **`SpecMeshTest`** - Concrete implementation for modifier/operator tests
   ```python
   test = SpecMeshTest(
       "my_test",
       "test_object",
       "expected_object",
       operations_stack=[
           ModifierSpec("subsurf", "SUBSURF", {"levels": 2}),
           OperatorSpecEditMode("bevel", {"offset": 0.1}, "EDGE", [1, 2, 3])
       ]
   )
   test.run_test()
   ```

6. **`BlendFileTest`** - Test modifiers already in a blend file
   ```python
   test = BlendFileTest("test_object", "expected_object")
   test.run_test()
   ```

7. **`GeoNodesSimulationTest`** - Test geometry nodes with simulation
   ```python
   test = GeoNodesSimulationTest(
       "test_object",
       "expected_object",
       frames_num=24
   )
   ```

8. **`RunTest`** - Execute multiple tests in a suite
   ```python
   tests = [
       SpecMeshTest("test1", "obj1", "exp1", [modifier_spec1]),
       SpecMeshTest("test2", "obj2", "exp2", [modifier_spec2]),
   ]
   runner = RunTest(tests)
   runner.run_all_tests()
   ```

**Features:**
- Automatic test/expected object comparison
- Support for `BLENDER_TEST_UPDATE=1` to update reference objects
- Verbose output with `BLENDER_VERBOSE=1`
- Supports meshes, curves, and lattices
- Automatic mesh validation
- Handles physics simulations (cloth, soft body, dynamic paint)
- Particle system testing

**Usage Example:**
```python
import unittest
from modules.mesh_test import (
    ModifierSpec,
    OperatorSpecEditMode,
    SpecMeshTest,
    RunTest,
)

class TestMyModifier(unittest.TestCase):
    def test_modifier_application(self):
        tests = [
            SpecMeshTest(
                "subdivision_test",
                "test_cube",
                "expected_cube",
                operations_stack=[
                    ModifierSpec("subsurf", "SUBSURF", {"levels": 2}),
                ],
            )
        ]
        runner = RunTest(tests)
        runner.run_all_tests()
```

---

### Rendering & Comparison

#### `render_report.py`

Framework for render testing with image comparison and HTML report generation.

**Key Classes:**
- `Report` - Main reporting class for render tests
- `TestResult` - Holds results for individual render tests

**Key Features:**
- Multi-threaded test execution
- Image comparison using oiiotool
- Automatic diff image generation (color and alpha)
- HTML report generation with image galleries
- Support for reference image updates
- Batch rendering support
- Device/configuration blocklists
- Comparison between render engines

**Usage:**
```python
from modules.render_report import Report

# Create report
report = Report(
    title="Cycles Test",
    output_dir="/path/to/output",
    oiiotool="/path/to/oiiotool"
)

# Configure
report.set_fail_threshold(0.016)  # Pixel difference threshold
report.set_fail_percent(1)         # Percentage of pixels that can differ
report.set_reference_dir("reference_renders")

# Run tests
def render_args(filepath, output):
    return [
        "--engine", "CYCLES",
        filepath,
        "--render-output", output,
        "--render-frame", "1",
    ]

success = report.run(
    "/path/to/test/files",
    "/path/to/blender",
    render_args,
    batch=True  # Batch multiple renders together
)
```

**Environment Variables:**
- `BLENDER_TEST_UPDATE=1` - Update reference images
- `BLENDER_VERBOSE=1` - Verbose output
- `BLENDER_TEST_COLOR=1` - Colored terminal output
- `BLENDER_TEST_IGNORE_BLOCKLIST=1` - Run all tests including known failures

---

#### `io_report.py`

Similar to render_report.py but for import/export testing.

**Usage:**
```python
from modules.io_report import IOReport

# Test file import/export
report = IOReport(output_dir="/path/to/output")
report.test_import("test.fbx", expected_data)
report.generate_html()
```

---

### Output & Display

#### `colored_print.py`

Colored terminal output for test results.

**Functions:**
- `use_message_colors()` - Enable ANSI color codes
- `print_message(message, type, status)` - Print formatted messages

**Usage:**
```python
from modules.colored_print import print_message, use_message_colors

# Enable colors (usually from BLENDER_TEST_COLOR env var)
use_message_colors()

# Print messages
print_message("Starting test...", 'SUCCESS', 'RUN')
print_message("Test passed", 'SUCCESS', 'OK')
print_message("Test failed", 'FAILURE', 'FAILED')
```

**Message Types:**
- `'SUCCESS'` - Green text
- `'FAILURE'` - Red text
- `None` - No color

**Status Options:**
- `'RUN'` - Running
- `'OK'` - Success
- `'PASSED'` - Test passed
- `'FAILED'` - Test failed

---

### Hardware & System Info

#### `gpu_info.py`

Retrieve GPU device information for tests.

**Usage:**
```python
# Run this script with Blender to get GPU info
# Used by render tests to detect device type
```

**Output:**
```
GPU_DEVICE_TYPE:NVIDIA
```

---

### Reporting

#### `global_report.py`

Global HTML report aggregating results from all test categories.

**Functions:**
- `add(output_dir, category, name, filepath, failed)` - Add test to global report
- `generate_html(output_dir)` - Generate index page

**Usage:**
```python
from modules import global_report

global_report.add(
    output_dir="/path/to/output",
    category="Render",
    name="Cycles CPU",
    filepath="cycles_cpu/report.html",
    failed=False
)
```

---

### Image Testing

#### `imbuf_test.py`

Utilities for image buffer testing.

**Usage:**
```python
from modules.imbuf_test import compare_images

# Compare two images
result = compare_images(image1, image2, threshold=0.01)
```

---

### Test Markers (NEW)

#### `test_markers.py`

Pytest-compatible test markers that also work with unittest.

**Available Markers:**

**Speed:**
- `@fast` - Fast tests (< 1 second)
- `@slow` - Slow tests (> 5 seconds)

**Resource Requirements:**
- `@gpu` - Requires GPU
- `@cpu_only` - CPU only
- `@memory_intensive` - High memory usage

**Categories:**
- `@unit` - Unit test
- `@integration` - Integration test
- `@regression` - Regression test
- `@smoke` - Smoke test

**Subsystems:**
- `@bmesh` - BMesh tests
- `@render` - Rendering tests
- `@animation` - Animation tests
- `@modifiers` - Modifier tests
- `@nodes` - Node system tests
- `@physics` - Physics simulation tests
- `@sculpt` - Sculpting tests
- `@geometry` - Geometry processing tests
- `@ui` - UI tests
- `@io` - Import/export tests

**Render Engines:**
- `@cycles` - Cycles specific
- `@eevee` - EEVEE specific
- `@workbench` - Workbench specific

**Platform:**
- `@wayland` - Wayland specific
- `@linux` / `@macos` / `@windows` - Platform specific

**Special:**
- `@screenshot` - Generates screenshots
- `@visual` - Visual comparison
- `@performance` - Performance test
- `@skip_in_ci` - Skip in CI
- `@flaky` - Known flaky test
- `@wip` - Work in progress
- `@debug` - Debug test

**Usage:**
```python
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "modules"))
from test_markers import unit, fast, bmesh, slow

class TestExample(unittest.TestCase):
    @unit
    @fast
    def test_quick(self):
        """Quick unit test."""
        self.assertEqual(1 + 1, 2)

    @unit
    @bmesh
    @slow
    def test_bmesh_operation(self):
        """Slow BMesh test."""
        import bmesh
        bm = bmesh.new()
        # ... test code ...
        bm.free()
```

**Class-Level Markers:**
```python
from test_markers import mark_class, unit, io, fast

@mark_class(unit, io, fast)
class TestIO(unittest.TestCase):
    """All methods automatically get unit, io, and fast markers."""

    def test_import(self):
        pass

    def test_export(self):
        pass
```

**Future pytest Integration:**
When tests are migrated to pytest:
```bash
# Run only unit tests
pytest -m "unit"

# Run fast tests only
pytest -m "fast"

# Run BMesh unit tests
pytest -m "bmesh and unit"

# Skip slow tests
pytest -m "not slow"

# Skip GPU and slow tests
pytest -m "not (gpu or slow)"
```

---

## Common Patterns

### Pattern 1: Simple Unit Test

```python
import unittest

class TestFeature(unittest.TestCase):
    def test_something(self):
        result = some_function()
        self.assertEqual(result, expected)
```

### Pattern 2: Modifier Test

```python
from modules.mesh_test import ModifierSpec, SpecMeshTest, RunTest

tests = [
    SpecMeshTest(
        "my_test",
        "test_object",
        "expected_object",
        operations_stack=[
            ModifierSpec("modifier_name", "MODIFIER_TYPE", {"param": value})
        ]
    )
]

runner = RunTest(tests)
runner.run_all_tests()
```

### Pattern 3: Render Test

```python
from modules.render_report import Report

report = Report("My Render Test", output_dir, oiiotool)
report.run(test_dir, blender, arguments_callback, batch=True)
```

### Pattern 4: Test with Temporary Files

```python
from modules.test_utils import with_tempdir

@with_tempdir
def test_file_operations(tempdir):
    test_file = tempdir / "test.blend"
    # ... test operations ...
    # tempdir automatically cleaned up
```

## Environment Variables

These environment variables affect test behavior:

- **`BLENDER_VERBOSE=1`** - Enable verbose test output
- **`BLENDER_TEST_UPDATE=1`** - Update reference images/objects
- **`BLENDER_TEST_COLOR=1`** - Enable colored terminal output
- **`BLENDER_TEST_IGNORE_BLOCKLIST=1`** - Run all tests including known failures
- **`LSAN_OPTIONS`** - Configure leak sanitizer
- **`ASAN_OPTIONS`** - Configure address sanitizer

## Best Practices

### 1. Use Existing Utilities

Don't reinvent the wheel - use existing utilities for common tasks:
- Use `mesh_test.py` for modifier/operator tests
- Use `render_report.py` for render comparisons
- Use `test_markers.py` for test categorization
- Use `colored_print.py` for formatted output

### 2. Keep Tests Isolated

```python
def setUp(self):
    """Reset Blender to factory defaults."""
    bpy.ops.wm.read_factory_settings()

def tearDown(self):
    """Clean up after test."""
    # Remove temporary objects, files, etc.
```

### 3. Use Descriptive Test Names

```python
def test_subdivision_modifier_with_catmull_clark_algorithm(self):
    """Test subdivision modifier using Catmull-Clark subdivision."""
    pass
```

### 4. Add Test Markers

```python
@unit
@fast
@modifiers
def test_my_feature(self):
    """Well-marked test for easy filtering."""
    pass
```

### 5. Handle Expected Failures

```python
import unittest

class TestFeature(unittest.TestCase):
    @unittest.expectedFailure
    def test_known_issue(self):
        """This test documents a known bug."""
        # This will pass if it fails, fail if it passes
        self.assertEqual(buggy_function(), expected)
```

### 6. Use Subtests for Multiple Cases

```python
def test_multiple_cases(self):
    """Test multiple inputs."""
    test_cases = [
        (input1, expected1),
        (input2, expected2),
        (input3, expected3),
    ]

    for input_val, expected in test_cases:
        with self.subTest(input=input_val):
            result = function(input_val)
            self.assertEqual(result, expected)
```

## Adding New Utilities

When adding new utility functions or classes:

1. **Choose the right module** - Add to existing module if related, create new if standalone
2. **Document thoroughly** - Include docstrings with usage examples
3. **Add type hints** - Use Python type hints for better IDE support
4. **Write tests** - Test your test utilities!
5. **Update this README** - Document new utilities here

### Template for New Utility Module

```python
# SPDX-FileCopyrightText: 2025 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Brief description of what this module does.

Usage example:
    from modules.my_utility import my_function

    result = my_function(param1, param2)
"""

import bpy
from typing import Optional, List


def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid

    Example:
        >>> my_function("test", 42)
        True
    """
    # Implementation
    pass


class MyUtilityClass:
    """Description of utility class."""

    def __init__(self, config: dict):
        """
        Initialize utility.

        Args:
            config: Configuration dictionary
        """
        self.config = config

    def process(self) -> None:
        """Process according to configuration."""
        pass
```

## Troubleshooting

### Import Errors

If you get import errors when trying to use these modules:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "modules"))
```

### Path Issues

Always use `pathlib.Path` for cross-platform path handling:

```python
from pathlib import Path

test_file = Path(__file__).parent / "test_data" / "test.blend"
```

### Test Isolation Issues

If tests affect each other:
1. Always use `--factory-startup`
2. Reset state in `setUp()`
3. Clean up in `tearDown()`
4. Use `with_tempdir` for file operations

## Resources

- **Main Test README**: [../README.md](../README.md)
- **Test Discovery Guide**: [../../AUTO_DISCOVERY_USAGE.md](../../AUTO_DISCOVERY_USAGE.md)
- **Python API Docs**: https://docs.blender.org/api/
- **unittest Documentation**: https://docs.python.org/3/library/unittest.html

---

*For questions or to report issues with test utilities, see the main tests README or ask on the developer forum.*
