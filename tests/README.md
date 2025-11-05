# Blender Test Suite

This directory contains Blender's comprehensive test suite, including unit tests, integration tests, rendering tests, performance benchmarks, and UI simulation tests.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Organization](#test-organization)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Categories](#test-categories)
- [Test Utilities](#test-utilities)
- [Debugging Tests](#debugging-tests)
- [CI/CD Integration](#cicd-integration)
- [Contributing](#contributing)

## Quick Start

### Running All Tests

```bash
# From build directory
ctest --output-on-failure

# Or from source root
make test
```

### Running Specific Tests

```bash
# Run a specific test by name
ctest -R bl_pyapi_bpy_path

# Run all BMesh tests
ctest -R bmesh

# Run with verbose output
ctest -V -R test_name
```

### Running Python Tests Directly

```bash
# Run a specific Python test with Blender
./blender --background --factory-startup --python tests/python/bl_pyapi_bpy_path.py -- --verbose

# Run with pytest (if migrated)
cd tests
pytest python/bl_pyapi_bpy_path.py -v
```

## Test Organization

```
tests/
├── python/              # Python-based tests (unittest)
│   ├── modules/         # Shared test utilities and helpers
│   ├── ui_simulate/     # UI interaction simulation tests
│   ├── bl_*.py          # Individual test files
│   └── CMakeLists.txt   # Test registration
├── gtests/              # C++ Google Test suite
│   ├── runner/          # Test runner executable
│   └── testing/         # Shared testing utilities
├── files/               # Test data and assets
│   ├── render/          # Reference render images
│   ├── io_tests/        # Import/export test files
│   ├── modeling/        # Modeling test assets
│   └── ...              # Other test data by category
├── performance/         # Performance benchmarking tests
│   ├── api/             # Benchmarking framework
│   └── tests/           # Individual benchmark tests
├── utils/               # Test utilities and helpers
│   ├── blender_headless.py  # Headless test runner
│   └── ...
├── coverage/            # Code coverage tools
├── blender_as_python_module/  # Tests for Blender as Python module
├── pytest.ini           # Pytest configuration
└── README.md            # This file
```

## Running Tests

### By Category

```bash
# Python API tests
ctest -R bl_pyapi

# Animation tests
ctest -R bl_animation

# Render tests
ctest -R render

# Cycles render tests
ctest -R cycles

# EEVEE render tests
ctest -R eevee

# UI simulation tests
ctest -R ui_
```

### By Speed

```bash
# Fast tests only (when pytest markers are used)
pytest -m fast

# Skip slow tests
pytest -m "not slow"

# Smoke tests only
pytest -m smoke
```

### Parallel Execution

```bash
# Run tests in parallel with ctest
ctest -j $(nproc)

# With pytest-xdist (if available)
pytest -n auto
```

### With Different Configurations

```bash
# Update reference images
BLENDER_TEST_UPDATE=1 ctest -R cycles

# Ignore blocklist (run all tests including known failures)
BLENDER_TEST_IGNORE_BLOCKLIST=1 ctest

# Enable verbose output
BLENDER_VERBOSE=1 ctest -R test_name

# Enable colored output
BLENDER_TEST_COLOR=1 ctest
```

## Writing Tests

### Python Tests (Current: unittest)

```python
# SPDX-FileCopyrightText: 2025 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

import unittest
import bpy

class TestMyFeature(unittest.TestCase):
    """Test description."""

    def setUp(self):
        """Set up test fixtures - runs before each test."""
        # Reset to factory defaults
        bpy.ops.wm.read_factory_settings()

    def tearDown(self):
        """Clean up after test - runs after each test."""
        pass

    def test_basic_functionality(self):
        """Test basic functionality of my feature."""
        # Arrange
        expected = "expected_value"

        # Act
        result = bpy.data.some_operation()

        # Assert
        self.assertEqual(result, expected)

    def test_edge_case(self):
        """Test edge case handling."""
        with self.assertRaises(ValueError):
            bpy.data.invalid_operation()

if __name__ == '__main__':
    import sys
    sys.argv = [__file__] + (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    unittest.main()
```

### Python Tests (Future: pytest)

```python
# SPDX-FileCopyrightText: 2025 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest
import bpy

@pytest.fixture
def clean_blender_scene():
    """Fixture providing a clean Blender scene."""
    bpy.ops.wm.read_factory_settings()
    yield
    # Cleanup happens automatically

@pytest.mark.unit
@pytest.mark.bmesh
def test_basic_functionality(clean_blender_scene):
    """Test basic functionality of my feature."""
    result = bpy.data.some_operation()
    assert result == "expected_value"

@pytest.mark.parametrize("input,expected", [
    ("case1", "result1"),
    ("case2", "result2"),
    ("case3", "result3"),
])
def test_multiple_cases(input, expected):
    """Test multiple cases with parametrization."""
    assert bpy.data.process(input) == expected
```

### Registering Tests in CMake

Tests are registered in `tests/python/CMakeLists.txt`:

```cmake
# Add a basic Blender test
add_blender_test(
  test_my_feature
  --python ${CMAKE_CURRENT_LIST_DIR}/bl_my_feature.py
)

# Add a test that needs test data
add_blender_test(
  test_with_data
  --python ${CMAKE_CURRENT_LIST_DIR}/bl_test_with_data.py
  --
  --testdir ${TEST_SRC_DIR}/my_test_data
)
```

## Test Categories

### Python Tests

| Category | Pattern | Description | Count |
|----------|---------|-------------|-------|
| **Python API** | `bl_pyapi_*.py` | Tests for Python API (bpy module) | ~15 |
| **Animation** | `bl_animation_*.py` | Animation and rigging tests | ~7 |
| **Blendfile** | `bl_blendfile_*.py` | File I/O and versioning tests | ~7 |
| **Geometry** | `bl_geometry_*.py` | Geometry processing tests | ~3 |
| **Modifiers** | `bl_mesh_modifiers.py` | Modifier system tests | ~1 |
| **I/O** | `bl_*_io_*.py` | Import/export tests | ~5 |
| **Rendering** | Render tests | Cycles, EEVEE, Workbench | Many |
| **UI** | `ui_simulate/*.py` | UI interaction tests | ~4 |

### Test Markers (for pytest)

When tests are migrated to pytest, use these markers:

```python
@pytest.mark.unit          # Fast unit test
@pytest.mark.integration   # Integration test
@pytest.mark.slow          # Slow test (>5 seconds)
@pytest.mark.gpu           # Requires GPU
@pytest.mark.bmesh         # BMesh subsystem
@pytest.mark.render        # Rendering test
@pytest.mark.cycles        # Cycles-specific
@pytest.mark.eevee         # EEVEE-specific
```

## Test Utilities

### Available Utilities

Located in `tests/python/modules/`:

- **`render_report.py`** - Render test comparison and HTML report generation
- **`io_report.py`** - I/O test reporting utilities
- **`test_utils.py`** - General test utilities
- **`mesh_test.py`** - Mesh validation utilities
- **`imbuf_test.py`** - Image buffer testing utilities
- **`colored_print.py`** - Colored console output
- **`global_report.py`** - Global test reporting

### Using Test Utilities

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from test_utils import some_utility_function
from mesh_test import validate_mesh
```

### Headless Test Runner

For UI tests without a display:

```bash
python tests/utils/blender_headless.py [blender_args]
```

## Debugging Tests

### Running a Single Test with Debug Output

```bash
# With verbose Blender output
BLENDER_VERBOSE=1 ctest -V -R test_name

# Run directly with Blender for more control
./blender --background --factory-startup --python tests/python/bl_test.py -- --verbose
```

### Using Python Debugger

```python
import unittest
import pdb

class TestMyFeature(unittest.TestCase):
    def test_something(self):
        # Set breakpoint
        pdb.set_trace()
        # ... test code ...
```

### Debugging with pytest

```bash
# Drop into debugger on failure
pytest tests/python/bl_test.py --pdb

# Drop into debugger at start of test
pytest tests/python/bl_test.py --trace
```

### Memory Leak Detection

Tests automatically run with ASAN/LSAN when built with sanitizers:

```bash
# Build with sanitizers
cmake -DWITH_COMPILER_ASAN=ON ..
make

# Run tests (leaks will be reported)
ctest
```

### UI Test Debugging

UI simulation tests support editor integration:

```bash
# Follow test execution in your editor (example with gvim)
./tests/python/ui_simulate/run.py \
    --blender=./blender \
    --tests test_undo.text_editor_simple \
    --step-command-pre='gvim --remote-silent +{line} "{file}"'
```

## CI/CD Integration

### Environment Variables

- **`TEST_BLENDER_EXE`** - Path to Blender executable
- **`TEST_PYTHON_EXE`** - Path to Python interpreter
- **`TEST_SRC_DIR`** - Test data directory
- **`TEST_OUT_DIR`** - Test output directory
- **`BLENDER_VERBOSE`** - Enable verbose output
- **`BLENDER_TEST_UPDATE`** - Update reference images
- **`BLENDER_TEST_COLOR`** - Enable colored output
- **`BLENDER_TEST_IGNORE_BLOCKLIST`** - Run all tests including known failures

### Running in CI

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    cd build
    ctest --output-on-failure -j $(nproc)
  env:
    BLENDER_TEST_COLOR: 1
```

## Code Coverage

### Generating Coverage Reports

```bash
# Build with coverage enabled
cmake -DWITH_COMPILER_CODE_COVERAGE=ON ..
make

# Run tests
ctest

# Generate coverage report
cd tests/coverage
python coverage.py report

# View in browser
python coverage.py show
```

### Coverage Commands

```bash
# Generate HTML report
make coverage-report

# Open report in browser
make coverage-show

# Reset coverage data
make coverage-reset
```

## Performance Testing

Performance tests are in `tests/performance/`:

```bash
# Run performance benchmarks
python tests/performance/benchmark.py --blender ./blender

# Run specific benchmark
python tests/performance/benchmark.py --blender ./blender --tests cycles
```

## Test Data

Test data is located in `tests/files/`:

- **Large files**: Consider using Git LFS for large test assets
- **Reference images**: Render test reference images in `tests/files/render/`
- **Test blend files**: Organized by category (modeling, animation, etc.)

### Updating Reference Images

When render output changes intentionally:

```bash
BLENDER_TEST_UPDATE=1 ctest -R cycles
git add tests/files/render/
git commit -m "Update reference renders for [reason]"
```

## Common Issues

### Test Fails Locally But Passes in CI

- Check for factory startup: tests should use `--factory-startup`
- Check for filesystem differences (paths, line endings)
- Check for display/GPU differences

### Test is Flaky

- Add to flaky test tracker (when available)
- Increase timeout
- Check for race conditions
- Add proper test isolation

### Reference Image Mismatch

- Check if change is intentional
- Update reference: `BLENDER_TEST_UPDATE=1 ctest -R test_name`
- Check diff images in test output directory

## Contributing

### Adding a New Test

1. Create test file: `tests/python/bl_mytest.py`
2. Follow existing patterns (see examples above)
3. Register in `tests/python/CMakeLists.txt`
4. Add test data to `tests/files/` if needed
5. Run and verify: `ctest -R mytest`
6. Commit both test and any reference data

### Test Naming Conventions

- **File names**: `bl_<category>_<feature>.py`
- **Test classes**: `Test<Feature>`
- **Test methods**: `test_<specific_case>`

### Best Practices

1. **Isolation**: Each test should be independent
2. **Factory startup**: Use `--factory-startup` or reset state
3. **Cleanup**: Clean up temporary files and objects
4. **Fast**: Keep tests fast; mark slow tests appropriately
5. **Descriptive**: Use clear test and assertion messages
6. **Coverage**: Test both success and failure cases
7. **Data**: Check in minimal test data; use parametrization

## Resources

- **Developer Docs**: https://developer.blender.org/docs/
- **Testing Guidelines**: https://developer.blender.org/docs/handbook/testing/
- **Python API**: https://docs.blender.org/api/
- **unittest docs**: https://docs.python.org/3/library/unittest.html
- **pytest docs**: https://docs.pytest.org/ (for future migration)

## Getting Help

- **Developer Forum**: https://devtalk.blender.org
- **Chat**: #blender-coders on blender.chat
- **Bug Reports**: https://projects.blender.org

---

*For more detailed information about specific test subsystems, see the README files in subdirectories.*
