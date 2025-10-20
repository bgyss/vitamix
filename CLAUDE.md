# CLAUDE.md

This document provides context and guidance for working with the Blender codebase using Claude Code.

## Project Overview

**Blender** is the free and open source 3D creation suite. It supports the entirety of the 3D pipeline—modeling, rigging, animation, simulation, rendering, compositing, motion tracking and video editing.

- **Primary Language**: C/C++
- **Python Integration**: Extensive Python API for scripting and add-ons
- **Build System**: CMake with convenience Makefile wrappers
- **License**: GNU GPL v3 (see [blender.org/about/license](https://www.blender.org/about/license))

## Repository Structure

```
/source/           # Main source code
  /blender/        # Core Blender modules
    /bmesh/        # BMesh (mesh editing data structure)
    /editors/      # Editor UI and operators
    /gpu/          # GPU/graphics subsystem
    /nodes/        # Node system (shaders, compositing, etc.)
    /compositor/   # Compositor system
    /geometry/     # Geometry processing
    /modifiers/    # Mesh/object modifiers
    /animrig/      # Animation rigging system
    /draw/         # Drawing/viewport code
    /imbuf/        # Image buffer library
    /makesdna/     # DNA structure generation (data definitions)
    /blenloader/   # File I/O (.blend files)
  /creator/        # Blender application entry point

/intern/           # Internal libraries
/extern/           # External dependencies
/scripts/          # Python scripts and modules
/release/          # Release-related files
/tests/            # Test suite
/build_files/      # Build system configurations
/doc/              # Documentation
/tools/            # Development tools
```

## Key Architectural Concepts

### DNA/RNA System
- **DNA (makesdna)**: Defines Blender's data structures for file I/O
- **RNA**: Runtime type system for accessing and manipulating data via Python

### Editor System
- Each editor type (3D View, Node Editor, etc.) has its own subdirectory in `source/blender/editors/`
- Editors contain operators, UI code, and event handlers

### BMesh
- Flexible mesh editing data structure used throughout Blender
- Located in `source/blender/bmesh/`

### Node System
- Unified node system for shaders, compositing, and geometry nodes
- Base system in `source/blender/nodes/`

## Development Setup

### Building Blender

See official build instructions: https://developer.blender.org/docs/handbook/building_blender/

Quick start (Linux/macOS):
```bash
make update    # Update submodules and libraries
make           # Build Blender (wrapper for CMake)
```

Windows:
```bash
make.bat update
make.bat
```

### Common Make Targets

```bash
make full          # Full rebuild
make debug         # Build with debug symbols
make release       # Build optimized release
make clean         # Clean build files
make test          # Run test suite
```

## Code Style and Conventions

### C/C++ Code
- Follow `.clang-format` configuration (use `clang-format` for formatting)
- See `.clang-tidy` for linting rules
- Code style: https://developer.blender.org/docs/handbook/code_style/

### Python Code
- PEP 8 style (configured in `pyproject.toml`)
- Python 3.11+ required

### Important Guidelines
- All new code must include SPDX license headers
- Use `BLI_` prefix for Blender library functions
- Use descriptive variable names (avoid single-letter except loops)
- Comment complex logic and non-obvious design decisions

## Finding Your Way Around

### Key Entry Points
- **Application start**: `source/creator/`
- **Main window management**: `source/blender/windowmanager/`
- **3D Viewport**: `source/blender/editors/space_view3d/`
- **Python API**: `source/blender/python/`

### Common Patterns
- **Operators**: Actions users can perform (undo-able operations)
- **RNA properties**: Exposed data that can be accessed from Python
- **DNA structs**: Data that gets saved to .blend files

### Searching the Codebase
- Use `BKE_` prefix for Blender Kernel functions (core functionality)
- Use `WM_` prefix for Window Manager functions
- Use `ED_` prefix for Editor functions
- Use `RNA_` prefix for RNA system functions
- Use `DNA_` prefix for DNA struct definitions

## Testing

```bash
# Run full test suite
make test

# Run specific tests
ctest -R <test_name>

# Python tests
./blender --python tests/python/<test_file>.py
```

Test locations:
- `tests/python/` - Python API tests
- `tests/gtests/` - Google Test (C++) tests

## Documentation Resources

- **Main Website**: http://www.blender.org
- **Developer Docs**: https://developer.blender.org/docs/
- **API Documentation**: https://docs.blender.org/api/
- **Developer Forum**: https://devtalk.blender.org
- **Code Review & Tracker**: https://projects.blender.org

## Common Tasks

### Adding a New Feature
1. Understand the relevant subsystem (see structure above)
2. Define DNA structs if new data needs to be saved
3. Define RNA properties for Python access
4. Implement core functionality (typically in `blenkernel/`)
5. Add UI/operators in appropriate editor
6. Add tests
7. Update documentation

### Debugging
- Use `printf` debugging or IDE debugger
- Enable debug build: `make debug`
- Python errors are printed to console
- Check console for warnings/errors

### Working with Python
- Blender's Python API is auto-generated from RNA
- Module structure: `bpy.data`, `bpy.ops`, `bpy.types`, `bpy.context`
- Scripts location: `scripts/modules/`, `scripts/startup/`

## Important Notes

- **Large Codebase**: Blender has millions of lines of code - focus on specific subsystems
- **Build Time**: First build can take 30+ minutes; incremental builds are faster
- **Submodules**: Run `make update` to sync external libraries and dependencies
- **Git Branches**: Development happens on `main` branch
- **Code Review**: All changes go through code review at projects.blender.org

## Tips for Claude Code Users

- When exploring specific features, start with the relevant editor in `source/blender/editors/`
- DNA struct names usually start with file type (e.g., `Object`, `Mesh`, `Scene`)
- Look for `_exec` functions to find operator implementations
- Check `RNA_def_*` functions to understand property definitions
- Python API mirrors the RNA structure closely

---

For more detailed information, see the [Developer Documentation](https://developer.blender.org/docs/).
