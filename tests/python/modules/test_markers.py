# SPDX-FileCopyrightText: 2025 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Test markers utility for categorizing and tagging tests.

This module provides decorators that work with both unittest and pytest,
allowing tests to be categorized and filtered. When used with pytest,
these become proper pytest markers. When used with unittest, they add
metadata that can be used for filtering.

Usage with unittest (current):
    from modules.test_markers import unit, bmesh, fast

    class TestBMesh(unittest.TestCase):
        @unit
        @bmesh
        @fast
        def test_bmesh_operation(self):
            ...

Usage with pytest (future):
    Tests will automatically work with pytest markers:
    pytest -m "bmesh and not slow"
"""

import functools
import sys

# Check if pytest is available
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False


def _make_marker(name, description=""):
    """Create a marker decorator that works with both unittest and pytest."""
    def decorator(func):
        # Add marker metadata to function
        if not hasattr(func, '_test_markers'):
            func._test_markers = []
        func._test_markers.append(name)

        # If pytest is available, apply its marker
        if HAS_PYTEST:
            marker = getattr(pytest.mark, name)
            func = marker(func)

        # Add to docstring for visibility
        if func.__doc__:
            func.__doc__ = f"{func.__doc__}\n[Markers: {', '.join(func._test_markers)}]"
        else:
            func.__doc__ = f"[Markers: {', '.join(func._test_markers)}]"

        return func
    decorator.__doc__ = description
    return decorator


# Test execution speed markers
fast = _make_marker('fast', 'Fast unit test (< 1 second)')
slow = _make_marker('slow', 'Slow test (> 5 seconds)')

# Resource requirement markers
gpu = _make_marker('gpu', 'Requires GPU')
cpu_only = _make_marker('cpu_only', 'CPU only test')
memory_intensive = _make_marker('memory_intensive', 'Requires significant memory')

# Test category markers
unit = _make_marker('unit', 'Unit test for individual functions/methods')
integration = _make_marker('integration', 'Integration test across components')
regression = _make_marker('regression', 'Regression test for bug fixes')
smoke = _make_marker('smoke', 'Critical smoke test')

# Subsystem markers
bmesh = _make_marker('bmesh', 'BMesh subsystem test')
render = _make_marker('render', 'Rendering test')
io = _make_marker('io', 'Import/export test')
animation = _make_marker('animation', 'Animation system test')
modifiers = _make_marker('modifiers', 'Modifier test')
nodes = _make_marker('nodes', 'Node system test')
physics = _make_marker('physics', 'Physics simulation test')
sculpt = _make_marker('sculpt', 'Sculpting test')
geometry = _make_marker('geometry', 'Geometry processing test')
ui = _make_marker('ui', 'User interface test')

# Render engine markers
cycles = _make_marker('cycles', 'Cycles render engine test')
eevee = _make_marker('eevee', 'EEVEE render engine test')
workbench = _make_marker('workbench', 'Workbench render engine test')

# Platform/backend specific
wayland = _make_marker('wayland', 'Requires Wayland')
linux = _make_marker('linux', 'Linux-specific test')
macos = _make_marker('macos', 'macOS-specific test')
windows = _make_marker('windows', 'Windows-specific test')

# Special test types
screenshot = _make_marker('screenshot', 'Generates screenshots')
visual = _make_marker('visual', 'Requires visual comparison')
performance = _make_marker('performance', 'Performance/benchmark test')
skip_in_ci = _make_marker('skip_in_ci', 'Skip in CI environment')
flaky = _make_marker('flaky', 'Known flaky test')

# Development/debugging
wip = _make_marker('wip', 'Work in progress')
debug = _make_marker('debug', 'Debugging test')


def get_test_markers(func):
    """Get all markers applied to a test function."""
    return getattr(func, '_test_markers', [])


def has_marker(func, marker_name):
    """Check if a test function has a specific marker."""
    return marker_name in get_test_markers(func)


def filter_tests_by_marker(test_suite, marker_name, exclude=False):
    """
    Filter tests in a unittest TestSuite by marker.

    Args:
        test_suite: unittest.TestSuite to filter
        marker_name: Name of marker to filter by
        exclude: If True, exclude tests with marker; if False, include only tests with marker

    Returns:
        New TestSuite with filtered tests
    """
    import unittest

    filtered = unittest.TestSuite()

    for test in test_suite:
        if isinstance(test, unittest.TestSuite):
            # Recursively filter sub-suites
            filtered.addTest(filter_tests_by_marker(test, marker_name, exclude))
        else:
            # Get the test method
            test_method = getattr(test, test._testMethodName)
            has_it = has_marker(test_method, marker_name)

            if exclude and not has_it:
                filtered.addTest(test)
            elif not exclude and has_it:
                filtered.addTest(test)

    return filtered


# Convenience function for marking entire test classes
def mark_class(*markers):
    """
    Class decorator to apply markers to all test methods in a class.

    Usage:
        @mark_class(unit, bmesh, fast)
        class TestBMesh(unittest.TestCase):
            def test_something(self):
                ...
    """
    def decorator(cls):
        for attr_name in dir(cls):
            if attr_name.startswith('test_'):
                attr = getattr(cls, attr_name)
                if callable(attr):
                    for marker in markers:
                        setattr(cls, attr_name, marker(attr))
        return cls
    return decorator


if __name__ == '__main__':
    # Example usage
    print("Test Markers Utility")
    print("=" * 50)
    print("\nAvailable markers:")

    marker_types = {
        'Speed': ['fast', 'slow'],
        'Resources': ['gpu', 'cpu_only', 'memory_intensive'],
        'Categories': ['unit', 'integration', 'regression', 'smoke'],
        'Subsystems': ['bmesh', 'render', 'io', 'animation', 'modifiers', 'nodes',
                       'physics', 'sculpt', 'geometry', 'ui'],
        'Render Engines': ['cycles', 'eevee', 'workbench'],
        'Platform': ['wayland', 'linux', 'macos', 'windows'],
        'Special': ['screenshot', 'visual', 'performance', 'skip_in_ci', 'flaky'],
        'Development': ['wip', 'debug'],
    }

    for category, markers in marker_types.items():
        print(f"\n{category}:")
        for marker in markers:
            marker_func = globals()[marker]
            print(f"  - {marker}: {marker_func.__doc__}")
