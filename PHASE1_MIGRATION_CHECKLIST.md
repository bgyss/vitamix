# Phase 1 Complete: Migration Checklist & Implementation Guide

**Date:** 2025-11-05
**Phase:** 1 - Analysis & Preparation
**Status:** ✅ COMPLETE

---

## Phase 1 Deliverables Summary

### ✅ Completed Tasks

1. **Comprehensive Format Usage Audit**
   - File: `PHASE1_FORMAT_AUDIT.md`
   - 172 code locations identified
   - 46 files requiring changes
   - Categorized by subsystem and priority

2. **Format Conversion Utilities**
   - File: `source/blender/gpu/GPU_format_conversion.hh`
   - Conversion functions for all 13 deprecated formats
   - Helper functions for validation
   - String utilities for debugging

3. **Deprecation Warnings**
   - File: `source/blender/gpu/GPU_format_deprecated.h`
   - Compile-time warnings (optional enable)
   - Runtime warning functions
   - Migration tracking macros

4. **Test Baseline & Strategy**
   - File: `PHASE1_TEST_BASELINE.md`
   - 15 GPU test files identified
   - Comprehensive testing strategy
   - Performance benchmarks defined

5. **Migration Plan**
   - File: `METAL_TEXTURE_FORMAT_MIGRATION_PLAN.md`
   - 8-phase implementation plan
   - 5-7 week timeline
   - Risk mitigation strategies

---

## Key Findings from Audit

### Most Critical Files (Must Fix First)

1. **gpu/vulkan/vk_data_conversion.cc** (77 locations)
   - Core format conversion logic
   - All 13 formats in multiple switch statements
   - CRITICAL for Vulkan backend

2. **compositor/intern/result.cc** (6 locations)
   - Real-time compositor format handling
   - CRITICAL for compositor pipeline

3. **render/intern/render_result.cc** (1 location)
   - Render output format selection
   - CRITICAL for render quality

4. **GPU_format.hh** (13 format definitions)
   - Core format enum declarations
   - CRITICAL - must be updated before anything else

### High Volume Areas

- **Gizmos:** 27 vertex attribute usages
- **Transform System:** 8 usages
- **View3D:** 12 usages
- **Draw System:** 20+ usages

### Deprecated Format Distribution

| Format | Usage Count | Primary Use Cases |
|--------|-------------|-------------------|
| SFLOAT_32_32_32 | 77 | Vertex positions, normals, colors |
| SFLOAT_16_16_16 | 16 | Texture data (half-float images) |
| All others | 7-8 each | Vulkan conversion switches |

---

## Migration Checklist by Phase

### Phase 2: Core GPU System ⏳

#### Part A: Format Definitions & Utilities

- [ ] **Update GPU_format.hh**
  - [ ] Add deprecation comments to 13 format macros
  - [ ] Prepare removal strategy
  - [ ] Document replacement formats

- [ ] **Update GPU_texture.hh**
  - [ ] Review TextureFormat enum
  - [ ] Review TextureTargetFormat enum
  - [ ] Review TextureWriteFormat enum
  - [ ] Add format validation

- [ ] **Test conversion utilities**
  - [ ] Unit test for `to_compatible_texture_format()`
  - [ ] Unit test for `is_deprecated_texture_format()`
  - [ ] Unit test for `texture_format_component_count()`

**Success Criteria:**
- ✅ Conversion utilities compile and pass tests
- ✅ Deprecation warnings can be enabled
- ✅ No breaking changes to API

---

#### Part B: Vulkan Backend (CRITICAL - 77 locations)

**File:** `source/blender/gpu/vulkan/vk_data_conversion.cc`

**Functions to Update:**

1. **`host_to_device_needs_conversion()`**
   - [ ] Lines 83, 88: Update SFLOAT format checks
   - [ ] Lines 110-180: Update switch cases for all 13 formats
   - [ ] Add conversion to 4-component equivalents

2. **`device_to_host_needs_conversion()`**
   - [ ] Lines 238-260: Update all switch cases
   - [ ] Handle 4-component → 4-component (no conversion)

3. **`to_component_len()`**
   - [ ] Lines 284-344: Update to return 4 for all formats
   - [ ] Or remove 3-component cases entirely

4. **`to_device_format()`**
   - [ ] Lines 398-420: Update format mappings
   - [ ] Map RGB → RGBA equivalents

5. **`to_host_format_conversion()`**
   - [ ] Lines 477-499: Update conversion logic
   - [ ] Handle padding for 4th component

6. **`to_texture_format_vulkan()`**
   - [ ] Lines 524-580: Update Vulkan format mappings
   - [ ] Verify VK_FORMAT_* equivalents

**Testing:**
- [ ] Run `vulkan/tests/vk_data_conversion_test.cc`
- [ ] Test on Vulkan-capable hardware
- [ ] Verify format conversion correctness
- [ ] Check for memory leaks

**Success Criteria:**
- ✅ All 77 locations updated
- ✅ Vulkan tests pass
- ✅ No device/host conversion errors

---

### Phase 3: Draw System ⏳

#### Part A: Mesh Extractors (9 locations)

- [ ] **extract_mesh_vbo_pos.cc** (Lines 74, 136)
  ```cpp
  // Change:
  VertAttrType::SFLOAT_32_32_32
  // To:
  VertAttrType::SFLOAT_32_32_32_32
  ```

- [ ] **extract_mesh_vbo_skin_roots.cc** (Line 28)
- [ ] **extract_mesh_vbo_lnor.cc** (Line 42)
- [ ] **extract_mesh_vbo_fdots_pos.cc** (Line 27)
- [ ] **extract_mesh_vbo_edituv_stretch_angle.cc** (Line 32)

**Testing:**
- [ ] Edit mode mesh display
- [ ] Sculpt mode rendering
- [ ] Vertex selection highlighting
- [ ] Face dot rendering

#### Part B: Draw Cache Implementations (15 locations)

- [ ] **draw_cache_impl_curve.cc** (4 locations)
- [ ] **draw_cache_impl_volume.cc** (3 locations)
- [ ] **draw_cache_impl_curves.cc** (2 locations)
- [ ] **draw_cache_impl_particles.cc**
- [ ] **draw_cache_impl_lattice.cc**
- [ ] **draw_cache_impl_grease_pencil.cc**
- [ ] **draw_pbvh.cc** (Line 285)

**Testing:**
- [ ] Curve object rendering
- [ ] Volume rendering
- [ ] Hair rendering
- [ ] Particle system display
- [ ] Lattice deformation visualization
- [ ] Grease Pencil strokes

**Success Criteria:**
- ✅ All draw cache files updated
- ✅ No visual regressions
- ✅ Performance within 5% baseline

---

### Phase 4: Rendering & Compositor ⏳

#### Part A: Compositor (6 locations)

**File:** `compositor/intern/result.cc`

- [ ] Line 184: Switch case for SFLOAT_32_32_32
- [ ] Line 201: Switch case for SFLOAT_32_32_32
- [ ] Line 216: Return SFLOAT_32_32_32 → Change to SFLOAT_32_32_32_32
- [ ] Line 245: Switch case for SFLOAT_32_32_32
- [ ] Line 271: Switch case for SFLOAT_32_32_32
- [ ] Line 574: Texture format selection

**Testing:**
- [ ] Compositor node execution
- [ ] Color management
- [ ] Multi-pass rendering
- [ ] Real-time preview

#### Part B: Render Results (1 location)

**File:** `render/intern/render_result.cc`

- [ ] Line 473: Format selection (half_float ? RGB16F : RGB32F)
  ```cpp
  // Change:
  use_half_float ? SFLOAT_16_16_16 : SFLOAT_32_32_32
  // To:
  use_half_float ? SFLOAT_16_16_16_16 : SFLOAT_32_32_32_32
  ```

**Testing:**
- [ ] Cycles render output
- [ ] EEVEE render output
- [ ] Render passes (diffuse, specular, normal, etc.)
- [ ] Multi-layer EXR export
- [ ] Half-float vs full-float renders

#### Part C: Screen Utilities (4 locations)

**File:** `editors/screen/glutil.cc`

- [ ] Line 79: Texture format SFLOAT_16_16_16
- [ ] Line 166: ELEM() check for SFLOAT_16_16_16
- [ ] Line 182: Texture format SFLOAT_16_16_16
- [ ] Line 476: format = TextureFormat::SFLOAT_16_16_16

**Testing:**
- [ ] Screen drawing
- [ ] UI rendering
- [ ] Thumbnail generation

**Success Criteria:**
- ✅ Color accuracy maintained (< 0.001% error)
- ✅ Alpha channel = 1.0 for opaque surfaces
- ✅ No color space issues
- ✅ Render output bit-for-bit identical (or within tolerance)

---

### Phase 5: Editors & Gizmos ⏳

#### Part A: Gizmo Library (27 locations)

**Files:**
- [ ] gizmo_types/dial3d_gizmo.cc (3 locations)
- [ ] gizmo_types/button2d_gizmo.cc (2 locations)
- [ ] gizmo_types/cage3d_gizmo.cc (5 locations)
- [ ] gizmo_types/cage2d_gizmo.cc (4 locations)
- [ ] gizmo_types/arrow3d_gizmo.cc (1 location)
- [ ] gizmo_types/move3d_gizmo.cc (1 location)
- [ ] gizmo_types/primitive3d_gizmo.cc (1 location)
- [ ] gizmo_draw_utils.cc (1 location)

**Pattern to update:**
```cpp
// Old:
uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);

// New:
uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32_32);
```

**Testing Checklist:**
- [ ] Move gizmo (X, Y, Z axes)
- [ ] Rotate gizmo (circles)
- [ ] Scale gizmo (boxes)
- [ ] Cage gizmo 2D (image/texture manipulation)
- [ ] Cage gizmo 3D (volume manipulation)
- [ ] Dial gizmo (rotation dial)
- [ ] Arrow gizmo (directional)
- [ ] Button gizmo (clickable)
- [ ] All gizmos interactive
- [ ] No visual glitches

#### Part B: Transform System (8 locations)

**Files:**
- [ ] transform_constraints.cc (4 locations)
- [ ] transform_mode_vert_slide.cc (1 location)
- [ ] transform_mode_edge_slide.cc (1 location)
- [ ] transform_snap.cc (2 locations)

**Testing:**
- [ ] Transform constraints (axis locking)
- [ ] Vertex slide visualization
- [ ] Edge slide visualization
- [ ] Snap indicators
- [ ] Constraint lines rendering

#### Part C: Space View3D (12 locations)

**Files:**
- [ ] view3d_gizmo_navigate_type.cc (4 locations)
- [ ] view3d_gizmo_ruler.cc (4 locations)
- [ ] view3d_cursor_snap.cc (2 locations)
- [ ] view3d_placement.cc (1 location)
- [ ] view3d_draw.cc (1 location)

**Testing:**
- [ ] Navigation gizmo (compass)
- [ ] Ruler tool
- [ ] 3D cursor snapping
- [ ] Object placement tool
- [ ] General viewport drawing

**Success Criteria:**
- ✅ All gizmos visible and functional
- ✅ Transform tools work correctly
- ✅ No interaction bugs
- ✅ Performance acceptable

---

### Phase 6: Remaining Editors ⏳

#### Part A: Other Editor Spaces (9 locations)

- [ ] space_sequencer/sequencer_preview_draw.cc (2 locations - includes TEXTURE format!)
- [ ] space_node/node_draw.cc (1 location)
- [ ] space_file/file_draw.cc (1 location)
- [ ] space_clip/clip_draw.cc (1 location)
- [ ] screen/area.cc (1 location)
- [ ] interface/interface_widgets.cc (1 location)

#### Part B: Sculpt, Paint, Mesh (15 locations)

- [ ] gpencil_legacy/annotate_draw.cc (2 locations)
- [ ] curves/intern/curves_draw.cc (1 location)
- [ ] object/object_remesh.cc (1 location)
- [ ] grease_pencil/intern/grease_pencil_image_render.cc (1 location)
- [ ] mesh/editmesh_knife.cc (1 location)
- [ ] mesh/editmesh_preselect_edgering.cc (1 location)
- [ ] mesh/editmesh_preselect_elem.cc (4 locations)
- [ ] curve/editcurve_paint.cc (1 location)
- [ ] sculpt_paint/paint_cursor.cc (1 location)
- [ ] sculpt_paint/curves_sculpt_ops.cc (1 location)
- [ ] sculpt_paint/sculpt_detail.cc (1 location)

**Testing:**
- [ ] Sequencer preview
- [ ] Node editor backdrop
- [ ] File browser
- [ ] Clip editor
- [ ] UI widgets
- [ ] Grease Pencil annotation
- [ ] Curve painting
- [ ] Remesh visualization
- [ ] Knife tool
- [ ] Edge ring preselection
- [ ] Vertex/edge preselection
- [ ] Sculpt cursor
- [ ] Curves sculpting

**Success Criteria:**
- ✅ All editor visualizations working
- ✅ No crashes
- ✅ Acceptable performance

---

### Phase 7: Window Manager & Python ⏳

#### Part A: Window Manager (5 locations)

- [ ] windowmanager/xr/intern/wm_xr_draw.cc (3 locations)
- [ ] windowmanager/xr/intern/wm_xr_operators.cc (1 location)
- [ ] windowmanager/intern/wm_playanim.cc (1 TEXTURE format location)
- [ ] windowmanager/intern/wm_draw.cc (1 location)

**Testing:**
- [ ] XR rendering (if hardware available)
- [ ] Animation playback
- [ ] Window drawing
- [ ] Multi-window setup

#### Part B: Python GPU API (2 locations)

- [ ] python/gpu/gpu_py_shader.cc (1 location)
- [ ] python/gpu/gpu_py_texture.cc (1 TEXTURE format string mapping)

**Changes needed:**
```python
# gpu_py_texture.cc - Line 73:
# Old:
{int(TextureFormat::SFLOAT_16_16_16), "RGB16F"},

# New:
{int(TextureFormat::SFLOAT_16_16_16_16), "RGBA16F"},
# Add deprecation warning for old string
```

**Testing:**
- [ ] Python texture creation
- [ ] Python GPU module import
- [ ] Python scripts using GPU API
- [ ] Addon compatibility

**Python Test Script:**
```python
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

# Test 1: Texture creation
tex = gpu.types.GPUTexture((256, 256), format='RGBA32F')
assert tex is not None

# Test 2: Vertex format
shader = gpu.shader.from_builtin('UNIFORM_COLOR')
vertices = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
batch = batch_for_shader(shader, 'TRIS', {"pos": vertices})
assert batch is not None

# Test 3: Draw
batch.draw(shader)
print("Python GPU API test passed!")
```

**Success Criteria:**
- ✅ Python API fully functional
- ✅ Deprecation warnings for old API
- ✅ Documentation updated
- ✅ Example scripts work

---

### Phase 8: Format Removal & Final Validation ⏳

#### Part A: Remove Deprecated Formats

- [ ] **GPU_format.hh**
  - [ ] Remove SNORM_8_8_8_ macro
  - [ ] Remove SNORM_16_16_16_ macro
  - [ ] Remove UNORM_8_8_8_ macro
  - [ ] Remove UNORM_16_16_16_ macro
  - [ ] Remove SINT_8_8_8_ macro
  - [ ] Remove SINT_16_16_16_ macro
  - [ ] Remove SINT_32_32_32_ macro
  - [ ] Remove UINT_8_8_8_ macro
  - [ ] Remove UINT_16_16_16_ macro
  - [ ] Remove UINT_32_32_32_ macro
  - [ ] Remove SFLOAT_16_16_16_ macro
  - [ ] Remove SFLOAT_32_32_32_ macro
  - [ ] Remove SRGBA_8_8_8_ macro

- [ ] **GPU_texture.hh**
  - [ ] Remove 3-component formats from TextureFormat enum
  - [ ] Remove from TextureTargetFormat enum
  - [ ] Remove from TextureWriteFormat enum
  - [ ] Update enum documentation

- [ ] **Clean up TODO comments**
  - [ ] Search and remove "TODO(fclem): Incompatible with metal"
  - [ ] Remove format deprecation comments
  - [ ] Update migration documentation

#### Part B: Update Tests

- [ ] Add test for format migration completeness
- [ ] Add test to prevent 3-component format re-introduction
- [ ] Update Vulkan conversion tests
- [ ] Update texture tests

#### Part C: Documentation

- [ ] Update GPU format documentation
- [ ] Document migration in CHANGELOG
- [ ] Update developer handbook
- [ ] Create migration guide for external developers

#### Part D: Final Validation

**Cross-Platform Testing:**
- [ ] Linux + OpenGL - All features work
- [ ] Linux + Vulkan - All features work
- [ ] macOS + Metal - All features work (native support!)
- [ ] Windows + OpenGL - All features work
- [ ] Windows + Vulkan - All features work

**Performance Validation:**
- [ ] Viewport FPS within 5% of baseline
- [ ] Render time within 3% of baseline
- [ ] Memory usage increased by expected ~33%
- [ ] No memory leaks detected

**Visual Validation:**
- [ ] Screenshot comparison test suite
- [ ] Color accuracy verification
- [ ] No rendering artifacts
- [ ] Alpha channel handled correctly

**Functional Validation:**
- [ ] All GPU unit tests pass
- [ ] Full Blender test suite passes
- [ ] No new crashes
- [ ] No regressions reported

---

## Quick Reference: File Update Count by Subsystem

| Subsystem | Files | Locations | Priority |
|-----------|-------|-----------|----------|
| GPU Core | 2 | 13 | CRITICAL |
| Vulkan Backend | 1 | 77 | CRITICAL |
| Compositor | 2 | 7 | CRITICAL |
| Draw System | 12 | 20+ | HIGH |
| Gizmos | 8 | 27 | HIGH |
| Transform | 4 | 8 | HIGH |
| View3D | 4 | 12 | HIGH |
| Other Editors | 15 | 24 | MEDIUM |
| Window Manager | 4 | 5 | MEDIUM |
| Python | 2 | 2 | MEDIUM |
| **TOTAL** | **46** | **172+** | |

---

## Migration Timeline

| Phase | Estimated Time | Status |
|-------|---------------|---------|
| Phase 1: Analysis | 3-4 days | ✅ COMPLETE |
| Phase 2: Core GPU | 4-5 days | ⏳ READY TO START |
| Phase 3: Draw System | 5-6 days | ⏳ PENDING |
| Phase 4: Rendering | 4-5 days | ⏳ PENDING |
| Phase 5: Editors | 5-6 days | ⏳ PENDING |
| Phase 6: Remaining | 2-3 days | ⏳ PENDING |
| Phase 7: WM/Python | 2-3 days | ⏳ PENDING |
| Phase 8: Validation | 3-4 days | ⏳ PENDING |
| **TOTAL** | **28-36 days** | **~5-7 weeks** |

---

## Success Criteria Summary

### Code Quality
- ✅ All 172 locations migrated
- ✅ All 13 deprecated formats removed
- ✅ Zero compilation errors
- ✅ Zero compiler warnings (strict mode)
- ✅ All TODO comments cleaned up

### Testing
- ✅ All GPU unit tests pass
- ✅ Full Blender test suite passes
- ✅ Cross-platform validation complete
- ✅ Performance within targets

### Performance
- ✅ Viewport FPS: ±5% baseline
- ✅ Render time: ±3% baseline
- ✅ Memory: +33% expected (acceptable)

### Compatibility
- ✅ Native Metal support (no emulation)
- ✅ Vulkan: 90%+ device support
- ✅ OpenGL: Full compatibility maintained
- ✅ Python API: Backward compatible with warnings

---

## Next Actions

### Immediate (Start Phase 2)

1. **Begin Core GPU System Migration**
   - Update GPU_format_conversion.hh (already done ✅)
   - Start Vulkan backend migration
   - Test conversion functions

2. **Set up continuous testing**
   - Build Blender with GPU tests
   - Run baseline tests
   - Set up automated testing

3. **Create migration branch**
   ```bash
   git checkout -b feature/metal-compatible-gpu-formats
   git add source/blender/gpu/GPU_format_conversion.hh
   git add source/blender/gpu/GPU_format_deprecated.h
   git commit -m "Phase 1: Add GPU format conversion utilities"
   ```

### Week 1-2 Goals

- [ ] Complete Phase 2A (Core GPU definitions)
- [ ] Complete Phase 2B (Vulkan backend - 77 locations)
- [ ] Begin Phase 3A (Draw system)

### Communication

- Document progress in weekly reports
- Flag blockers immediately
- Request code review for critical sections
- Update migration plan with actual vs. estimated time

---

## Phase 1 Status: ✅ COMPLETE

**Deliverables:**
1. ✅ Comprehensive audit (172 locations, 46 files)
2. ✅ Format conversion utilities
3. ✅ Deprecation warning system
4. ✅ Test baseline & strategy
5. ✅ Migration checklist & guide

**Ready to proceed with Phase 2: Core GPU System Migration**

---

**Last Updated:** 2025-11-05
**Next Review:** Start of Phase 2
