# Phase 1: GPU Test Baseline & Testing Strategy

**Date:** 2025-11-05
**Purpose:** Establish baseline for GPU format migration testing

---

## Existing GPU Test Suite

### Test Files Identified

1. **texture_test.cc** - Texture creation, reading, writing, clearing
2. **immediate_test.cc** - Immediate mode rendering tests
3. **vertex_buffer_test.cc** - Vertex buffer management
4. **index_buffer_test.cc** - Index buffer operations
5. **framebuffer_test.cc** - Framebuffer operations
6. **shader_test.cc** - Shader compilation and usage
7. **buffer_texture_test.cc** - Buffer textures
8. **state_blend_test.cc** - Blending state
9. **compute_test.cc** - Compute shader tests
10. **storage_buffer_test.cc** - Storage buffers
11. **push_constants_test.cc** - Push constants
12. **specialization_constants_test.cc** - Specialization constants
13. **shader_create_info_test.cc** - Shader creation info
14. **shader_preprocess_test.cc** - Shader preprocessing
15. **gpu_testing.cc** - Test infrastructure

### Vulkan-Specific Tests
- **vulkan/tests/vk_data_conversion_test.cc** - Format conversion testing

---

## Current Test Coverage

### texture_test.cc Analysis

From the source code, existing tests use:
- ✅ `TextureFormat::UINT_32_32_32_32` (4-component, compatible)
- ✅ `TextureFormat::UINT_16_16_16_16` (4-component, compatible)
- ✅ `TextureFormat::SFLOAT_32_32_32_32` (4-component, compatible)

**Good news:** The texture tests already use 4-component formats!

### Test Flags Observed

```cpp
#define RUN_UNSUPPORTED false
#define RUN_SRGB_UNIMPLEMENTED false
#define RUN_NON_STANDARD_UNIMPLEMENTED false
#define RUN_COMPONENT_UNIMPLEMENTED false
```

**Note:** Some tests are disabled for unsupported formats. This suggests the test infrastructure already handles platform differences.

---

## Test Execution Strategy

### Phase 1: Pre-Migration Baseline (Current Phase)

**Goal:** Document expected behavior before changes

#### Step 1: Identify GPU Test Infrastructure
- [x] Located GPU test files in `source/blender/gpu/tests/`
- [x] Found Vulkan conversion tests
- [x] Identified test framework (Google Test based)

#### Step 2: Build Test Suite (If Possible)
```bash
# Full Blender build with tests:
make update
make test

# Or with CMake directly:
cd build
cmake .. -DWITH_GTESTS=ON
make
ctest -R gpu  # Run only GPU tests
```

#### Step 3: Document Current Test Results
- Expected: All tests pass with current 3-component format emulation
- Baseline: Test execution time, memory usage

### Phase 2: During Migration Testing

**Goal:** Ensure no regressions as we migrate

#### For Each Subsystem Migration:

1. **Unit Tests**
   - Run GPU test suite after each change
   - Verify format conversion correctness
   - Check for memory leaks

2. **Integration Tests**
   - Test affected features in actual Blender
   - Visual inspection for rendering artifacts

3. **Regression Tests**
   - Compare screenshots before/after
   - Verify numerical accuracy (colors, positions)

### Phase 3: Post-Migration Validation

**Goal:** Comprehensive validation of completed migration

#### Cross-Platform Testing
- Linux + OpenGL
- Linux + Vulkan
- macOS + Metal
- Windows + OpenGL
- Windows + Vulkan
- Windows + DirectX (if supported)

#### Performance Benchmarks
- Viewport FPS (3D view with complex scene)
- Render time (Cycles & EEVEE)
- Memory usage (track 33% increase from 3→4 components)
- GPU memory usage

---

## Testing Checklist by Category

### Category 1: Core GPU System

**Files:**
- `gpu/GPU_format.hh` - Format definitions
- `gpu/GPU_texture.hh` - Texture format enums
- `gpu/intern/gpu_texture.cc` - Texture creation

**Tests:**
- [ ] `texture_test.cc` - All tests pass
- [ ] Texture creation with 4-component formats
- [ ] Texture read/write correctness
- [ ] Format conversion accuracy

**Validation:**
- [ ] No compilation errors
- [ ] All enum values accessible
- [ ] Backward compatibility maintained

---

### Category 2: Vulkan Backend

**Files:**
- `gpu/vulkan/vk_data_conversion.cc` - 77 locations

**Tests:**
- [ ] `vulkan/tests/vk_data_conversion_test.cc`
- [ ] Host↔Device conversion correctness
- [ ] Component count calculations
- [ ] Format mapping validation

**Validation:**
- [ ] All switch cases handle 4-component formats
- [ ] No missing enum values
- [ ] Conversion performance acceptable

---

### Category 3: Draw System

**Files:**
- `draw/intern/draw_cache_impl_*.cc` (7 files)
- `draw/intern/mesh_extractors/*.cc` (5+ files)
- `draw/intern/draw_pbvh.cc`

**Tests:**
- [ ] Mesh rendering in 3D viewport
- [ ] Edit mode mesh display
- [ ] Sculpt mode rendering
- [ ] Curve/Bezier rendering
- [ ] Volume rendering
- [ ] Hair/Curves rendering
- [ ] Grease Pencil rendering

**Validation:**
- [ ] Visual inspection (no artifacts)
- [ ] Position data accuracy
- [ ] Normal data accuracy
- [ ] Vertex color accuracy
- [ ] Performance within 5% baseline

---

### Category 4: Editors & Gizmos

**Files:**
- `editors/gizmo_library/gizmo_types/*.cc` (7 files)
- `editors/transform/*.cc` (4 files)
- `editors/space_view3d/*.cc` (4 files)

**Tests:**
- [ ] Move gizmo rendering
- [ ] Rotate gizmo rendering
- [ ] Scale gizmo rendering
- [ ] Cage gizmos (2D/3D)
- [ ] Dial gizmo
- [ ] Arrow gizmo
- [ ] Button gizmo
- [ ] Transform constraints visualization
- [ ] Snap cursor rendering
- [ ] Ruler tool rendering
- [ ] Navigation gizmo

**Validation:**
- [ ] All gizmos visible
- [ ] Gizmo interaction works
- [ ] No visual glitches
- [ ] Performance acceptable

---

### Category 5: Rendering & Compositor

**Files:**
- `compositor/intern/result.cc` - 6 locations
- `render/intern/render_result.cc` - 1 location
- `editors/screen/glutil.cc` - 4 locations

**Tests:**
- [ ] Compositor node tree execution
- [ ] Render output (Cycles)
- [ ] Render output (EEVEE)
- [ ] Render passes (diffuse, specular, etc.)
- [ ] Image color accuracy
- [ ] Float/Half-float format handling
- [ ] Color management (OCIO)

**Validation:**
- [ ] Numerical accuracy (<0.001% error)
- [ ] No color shifts
- [ ] Alpha channel correct (new 4th component)
- [ ] File output correct

**Critical Tests:**
1. Render a test scene with known RGB values
2. Export as EXR (32-bit float)
3. Verify pixel values unchanged
4. Check alpha=1.0 for opaque surfaces

---

### Category 6: Python GPU API

**Files:**
- `python/gpu/gpu_py_texture.cc`
- `python/gpu/gpu_py_shader.cc`

**Tests:**
- [ ] Python texture creation
- [ ] Python vertex format usage
- [ ] Python GPU module import
- [ ] Format string mappings ("RGB16F" → "RGBA16F")

**Test Script:**
```python
import gpu
from gpu_extras.batch import batch_for_shader

# Test texture creation
texture = gpu.types.GPUTexture((256, 256), format='RGBA32F')  # Was RGB32F

# Test vertex format
shader = gpu.shader.from_builtin('UNIFORM_COLOR')
batch = batch_for_shader(shader, 'TRIS', {"pos": vertices})  # 3-component → 4-component

# Verify no crashes
batch.draw(shader)
```

**Validation:**
- [ ] No Python API breakage
- [ ] Deprecation warnings shown (if old API used)
- [ ] Documentation updated

---

### Category 7: XR & Window Manager

**Files:**
- `windowmanager/xr/intern/*.cc` (2 files)
- `windowmanager/intern/wm_playanim.cc`
- `windowmanager/intern/wm_draw.cc`

**Tests:**
- [ ] XR rendering (if hardware available)
- [ ] Animation playback
- [ ] Window drawing/overlay
- [ ] Multi-window rendering

**Validation:**
- [ ] XR viewport renders correctly
- [ ] Animation playback smooth
- [ ] No window drawing artifacts

---

## Performance Baseline

### Expected Performance Impact

**Memory Usage:**
- 3-component RGB: 12 bytes (float) or 6 bytes (half)
- 4-component RGBA: 16 bytes (float) or 8 bytes (half)
- **Increase:** ~33% more memory

**Bandwidth:**
- Memory bandwidth increases proportionally
- May impact performance on bandwidth-limited GPUs

**Computation:**
- GPU operations on 4-component data may be faster (better alignment)
- Potential speedup on some operations

**Target:**
- Overall performance within ±5% of baseline
- Memory increase acceptable for compatibility gain

### Benchmark Tests

1. **Viewport FPS Test**
   ```
   Scene: Default scene with subdivided monkey (Suzanne)
   Action: Rotate viewport continuously
   Metric: Average FPS over 30 seconds
   Baseline: [To be measured]
   Post-migration: [Should be within 5%]
   ```

2. **Render Time Test**
   ```
   Scene: Standard benchmark scene
   Cycles: 128 samples, GPU rendering
   Metric: Total render time
   Baseline: [To be measured]
   Post-migration: [Should be within 3%]
   ```

3. **Memory Usage Test**
   ```
   Scene: Large mesh (1M vertices)
   Metric: GPU memory usage (Blender stats panel)
   Baseline: [To be measured]
   Post-migration: [Expected +33% for vertex buffers]
   ```

---

## Test Automation Strategy

### Continuous Integration Tests

1. **Compilation Tests**
   - Build with all backends (OpenGL, Vulkan, Metal)
   - Zero warnings (with strict settings)
   - Zero errors

2. **Unit Tests**
   - Run full GPU test suite
   - All tests pass
   - No test skips

3. **Visual Regression Tests**
   - Screenshot comparison for key features
   - Pixel-perfect matching (or <1% difference)
   - Automated diffing

### Manual Testing Protocol

For each major subsystem migration:

1. **Pre-Migration**
   - Take screenshots of key features
   - Record performance metrics
   - Document any known issues

2. **Post-Migration**
   - Repeat screenshot capture
   - Re-measure performance
   - Compare side-by-side

3. **Sign-Off**
   - Visual inspection: Pass/Fail
   - Performance: Within target
   - Functionality: All features work

---

## Risk Areas Requiring Extra Testing

### High Risk (Test Extensively)

1. **Compositor Real-Time Preview**
   - Complex node trees
   - Multiple format conversions
   - Color management

2. **Render Output**
   - External render engines
   - Custom render passes
   - Multi-layer EXR export

3. **Vulkan Backend**
   - Most code changes (77 locations)
   - Format conversion logic
   - Platform-specific behavior

### Medium Risk (Test Thoroughly)

1. **Gizmo Rendering**
   - Many files changed (27 locations)
   - User interaction critical
   - Visual feedback important

2. **Transform Visualization**
   - Constraints display
   - Snapping indicators
   - Edge/vertex slide preview

3. **Draw System**
   - Mesh extractors
   - Draw caches
   - PBVH rendering

### Low Risk (Standard Testing)

1. **Individual Editor Visualizations**
   - Isolated changes
   - Less critical functionality

2. **Python API**
   - Backward compatibility maintained
   - Deprecation warnings added

---

## Bug Reporting Template

If issues are found during testing:

```markdown
### Format Migration Issue Report

**Subsystem:** [e.g., Compositor, Gizmos, Vulkan Backend]
**Affected Files:** [list files]
**Migration Phase:** [e.g., Phase 3A - Draw System]

**Expected Behavior:**
[Description]

**Actual Behavior:**
[Description with screenshots if visual]

**Reproduction Steps:**
1. [Step 1]
2. [Step 2]
3. [etc.]

**Environment:**
- OS: [Linux/macOS/Windows]
- GPU: [model]
- Backend: [OpenGL/Vulkan/Metal]
- Blender Build: [commit hash]

**Severity:**
- [ ] Critical (crash, data loss)
- [ ] High (feature broken)
- [ ] Medium (visual artifact)
- [ ] Low (minor issue)

**Proposed Fix:**
[If known]
```

---

## Test Results Documentation

### Pre-Migration Baseline

**Date:** [To be filled]
**Commit:** [hash]
**Platform:** [OS + GPU]

| Test Category | Pass | Fail | Skip | Notes |
|---------------|------|------|------|-------|
| GPU Core | - | - | - | [To be measured] |
| Vulkan Backend | - | - | - | [To be measured] |
| Draw System | - | - | - | [To be measured] |
| Editors | - | - | - | [To be measured] |
| Rendering | - | - | - | [To be measured] |
| Python API | - | - | - | [To be measured] |
| **Total** | **-** | **-** | **-** | |

### Post-Migration Results

**Date:** [After Phase 8]
**Commit:** [hash]
**Platform:** [OS + GPU]

| Test Category | Pass | Fail | Skip | Notes |
|---------------|------|------|------|-------|
| GPU Core | - | - | - | [To be measured] |
| Vulkan Backend | - | - | - | [To be measured] |
| Draw System | - | - | - | [To be measured] |
| Editors | - | - | - | [To be measured] |
| Rendering | - | - | - | [To be measured] |
| Python API | - | - | - | [To be measured] |
| **Total** | **-** | **-** | **-** | |

**Regression Count:** [Number of new failures]
**Performance Delta:** [% change]
**Memory Delta:** [% change]

---

## Next Steps

1. ✅ Document test infrastructure
2. ⏳ Build Blender with GPU tests enabled (optional, time-consuming)
3. ⏳ Run baseline tests and record results (when build available)
4. ✅ Create testing strategy for each migration phase
5. ⏳ Set up automated visual regression testing

---

## Summary

- **15 GPU test files** identified
- **Existing tests** already use 4-component formats (good sign!)
- **Comprehensive testing strategy** defined for all 8 migration phases
- **Performance targets** established (±5% acceptable)
- **Risk areas** identified for extra scrutiny

**Status:** Test baseline documentation complete. Actual test execution requires Blender build, which can be done during Phase 2+ migration.

**Recommendation:** Proceed with Phase 2 (Core GPU System migration) while building Blender in parallel for testing.
