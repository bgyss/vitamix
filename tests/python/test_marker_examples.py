# SPDX-FileCopyrightText: 2025 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Example file demonstrating test marker usage.

This file shows how to use test markers for categorization. These markers
work with both unittest (current) and pytest (future migration).

Run specific marker groups with pytest (when migrated):
  pytest -m "unit and fast"           # Fast unit tests only
  pytest -m "bmesh"                   # All BMesh tests
  pytest -m "not slow"                # Skip slow tests
  pytest -m "unit and not gpu"        # Unit tests that don't need GPU
"""

import unittest
import sys
import os

# Add modules directory to path for test utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "modules"))
from test_markers import (
    # Speed markers
    fast, slow,
    # Category markers
    unit, integration, smoke,
    # Subsystem markers
    bmesh, render, animation, io,
    # Resource markers
    gpu, memory_intensive,
    # Special markers
    flaky, skip_in_ci, wip,
    # Class marker decorator
    mark_class,
)


# Example 1: Simple unit test with markers
class TestBasicMarkers(unittest.TestCase):
    """Example of basic marker usage."""

    @unit
    @fast
    def test_fast_unit_test(self):
        """A fast unit test."""
        self.assertEqual(1 + 1, 2)

    @unit
    @slow
    def test_slow_unit_test(self):
        """A slow unit test that might take time."""
        # Simulate slow operation
        result = sum(range(1000))
        self.assertEqual(result, 499500)


# Example 2: Subsystem-specific tests
class TestBMeshOperations(unittest.TestCase):
    """Example of BMesh subsystem tests."""

    @unit
    @bmesh
    @fast
    def test_bmesh_create(self):
        """Test BMesh creation."""
        import bmesh
        bm = bmesh.new()
        self.assertIsNotNone(bm)
        bm.free()

    @integration
    @bmesh
    @slow
    def test_bmesh_complex_operation(self):
        """Test complex BMesh operations."""
        import bmesh
        bm = bmesh.new()
        # Complex operations...
        bm.free()
        self.assertTrue(True)


# Example 3: GPU-dependent tests
class TestGPURendering(unittest.TestCase):
    """Example of GPU-dependent tests."""

    @render
    @gpu
    @slow
    def test_gpu_render(self):
        """Test that requires GPU."""
        # This test would require GPU
        self.skipTest("GPU tests require special setup")

    @render
    @gpu
    @flaky
    def test_flaky_gpu_test(self):
        """Known flaky test marked appropriately."""
        # This test is known to be flaky
        self.skipTest("Marked as flaky - needs investigation")


# Example 4: Multiple markers for categorization
class TestAnimationSystem(unittest.TestCase):
    """Example of animation tests with multiple markers."""

    @smoke
    @animation
    @fast
    def test_animation_smoke(self):
        """Critical smoke test for animation."""
        import bpy
        # Quick smoke test
        self.assertTrue(hasattr(bpy.ops, 'anim'))

    @integration
    @animation
    @slow
    def test_animation_complex(self):
        """Complex animation test."""
        # Complex test
        self.skipTest("Example only")


# Example 5: Using class decorator to mark all tests
@mark_class(unit, io, fast)
class TestIOOperations(unittest.TestCase):
    """All tests in this class automatically get unit, io, and fast markers."""

    def test_import_operation(self):
        """Test import operation."""
        self.assertTrue(True)

    def test_export_operation(self):
        """Test export operation."""
        self.assertTrue(True)


# Example 6: Work in progress tests
class TestWorkInProgress(unittest.TestCase):
    """Example of WIP tests."""

    @wip
    @unit
    def test_under_development(self):
        """Test that's still being developed."""
        self.skipTest("Work in progress")


# Example 7: CI-specific handling
class TestCIBehavior(unittest.TestCase):
    """Example of CI-specific test handling."""

    @skip_in_ci
    @memory_intensive
    def test_memory_heavy(self):
        """Test that's too heavy for CI."""
        # Large memory operation
        self.skipTest("Skipped in CI - too memory intensive")


if __name__ == '__main__':
    # When running directly, you can filter by markers
    # In the future with pytest, this is automatic

    # Print marker information
    print("\n" + "=" * 70)
    print("TEST MARKER EXAMPLES")
    print("=" * 70)
    print("\nThis file demonstrates test marker usage patterns.")
    print("Markers help categorize and filter tests.")
    print("\nWith pytest (future), run:")
    print("  pytest -m 'unit'              # Run only unit tests")
    print("  pytest -m 'fast'              # Run only fast tests")
    print("  pytest -m 'bmesh and unit'    # BMesh unit tests")
    print("  pytest -m 'not slow'          # Skip slow tests")
    print("  pytest -m 'not (gpu or slow)' # Fast CPU-only tests")
    print("\nWith unittest (current), all tests run normally.")
    print("=" * 70 + "\n")

    # Run tests normally
    sys.argv = [__file__] + (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    unittest.main()
