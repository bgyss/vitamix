# Metal-Incompatible GPU Texture Formats Migration Plan

**Issue:** Remove 13 Metal-incompatible GPU texture formats from Blender codebase
**Priority:** High
**Impact:** Cross-platform compatibility (macOS Metal, Vulkan)
**Scope:** 75+ files across rendering pipeline

---

## Problem Statement

Blender's GPU subsystem contains 13 texture formats marked as `"TODO(fclem): Incompatible with metal, to remove"` in `source/blender/gpu/GPU_texture.hh`. These 3-component (RGB) formats have poor hardware support:
- **<5% device support** on Vulkan
- **Requires emulation** on Metal (macOS)
- **90%+ support** for 4-component (RGBA) equivalents

## Deprecated Formats

### Texture Formats to Remove
1. SNORM_8_8_8
2. SNORM_16_16_16
3. UNORM_8_8_8
4. UNORM_16_16_16
5. SINT_8_8_8
6. SINT_16_16_16
7. SINT_32_32_32
8. UINT_8_8_8
9. UINT_16_16_16
10. UINT_32_32_32
11. SFLOAT_16_16_16
12. SFLOAT_32_32_32
13. SRGBA_8_8_8

### Migration Mapping

| Deprecated Format | Replacement Format |
|-------------------|-------------------|
| SNORM_8_8_8 | SNORM_8_8_8_8 |
| SNORM_16_16_16 | SNORM_16_16_16_16 |
| UNORM_8_8_8 | UNORM_8_8_8_8 |
| UNORM_16_16_16 | UNORM_16_16_16_16 |
| SINT_8_8_8 | SINT_8_8_8_8 |
| SINT_16_16_16 | SINT_16_16_16_16 |
| SINT_32_32_32 | SINT_32_32_32_32 |
| UINT_8_8_8 | UINT_8_8_8_8 |
| UINT_16_16_16 | UINT_16_16_16_16 |
| UINT_32_32_32 | UINT_32_32_32_32 |
| SFLOAT_16_16_16 | SFLOAT_16_16_16_16 |
| SFLOAT_32_32_32 | SFLOAT_32_32_32_32 |
| SRGBA_8_8_8 | SRGBA_8_8_8_8 |

---

## Affected Files by Subsystem

### Draw System (25 files)
- `draw/intern/draw_cache_impl_*.cc` (curve, volume, curves, particles, lattice, grease_pencil)
- `draw/intern/draw_pbvh.cc`
- `draw/intern/mesh_extractors/extract_mesh_vbo_*.cc` (pos, lnor, skin_roots, fdots_pos, edituv_stretch_angle)
- `draw/engines/eevee/*.cc`
- `draw/engines/overlay/*.hh`

### Compositor (2 files)
- `compositor/intern/result.cc`
- `compositor/cached_resources/intern/ocio_color_space_conversion_shader.cc`

### Rendering (2 files)
- `render/intern/render_result.cc`
- `imbuf/opencolorio/intern/libocio/libocio_gpu_shader_binder.cc`

### Editors (30 files)
- `editors/space_view3d/*.cc` (draw, gizmos, placement, cursor_snap, ruler)
- `editors/sculpt_paint/*.cc` (paint_cursor, curves_sculpt_ops, sculpt_detail)
- `editors/transform/*.cc` (snap, vert_slide, edge_slide, constraints)
- `editors/gizmo_library/gizmo_types/*.cc` (all gizmo types)
- `editors/interface/interface_widgets.cc`
- `editors/grease_pencil/intern/*.cc`

### GPU Core (10 files)
- `gpu/GPU_format.hh`
- `gpu/GPU_texture.hh`
- `gpu/intern/gpu_*.cc` (texture, vertex_format, immediate, batch_utils, batch_presets)
- `gpu/opengl/gl_texture.{cc,hh}`
- `gpu/vulkan/vk_*.cc` (texture, data_conversion, common)
- `gpu/tests/*.cc`

### Other (6 files)
- `windowmanager/intern/*.cc` (wm_playanim, wm_draw)
- `windowmanager/xr/intern/*.cc`
- `python/gpu/*.cc`

---

## Implementation Plan

### Phase 1: Analysis & Preparation
**Duration:** 3-4 days

#### Tasks:
1. ✓ Audit all 75+ files using deprecated formats
2. Create format conversion utility functions
3. Add compile-time deprecation warnings
4. Establish GPU test baseline
5. Document current behavior for regression testing

#### Deliverables:
- Complete file audit spreadsheet
- Format conversion utility in `gpu/intern/gpu_format_conversion.cc`
- Test baseline report

---

### Phase 2: Core GPU Subsystem
**Duration:** 4-5 days

#### Tasks:
1. Update texture format enums in `GPU_texture.hh`
   - Remove 3-component formats from `TextureFormat`
   - Remove from `TextureTargetFormat`
   - Remove from `TextureWriteFormat`

2. Update `GPU_format.hh` definitions
   - Remove `*_8_8_8_()` macro definitions
   - Remove `*_16_16_16_()` macro definitions
   - Remove `*_32_32_32_()` macro definitions
   - Remove `SRGBA_8_8_8_()`

3. Update vertex format handling
   - Modify `gpu/intern/gpu_vertex_format.cc`
   - Ensure proper 4-component alignment
   - Update padding calculations

4. Update backend implementations
   - OpenGL: `gpu/opengl/gl_texture.cc`
   - Vulkan: `gpu/vulkan/vk_texture.cc`, `vk_data_conversion.cc`
   - Metal: Format mappings (if accessible)

#### Testing:
- Run `gpu/tests/texture_test.cc`
- Run `gpu/tests/immediate_test.cc`
- Verify no compilation errors

---

### Phase 3: Draw System Migration
**Duration:** 5-6 days

#### Tasks:

**3.1 Mesh Extractors**
Files to update:
- `draw/intern/mesh_extractors/extract_mesh_vbo_pos.cc`
  - Line 74, 136: Change `SFLOAT_32_32_32` → `SFLOAT_32_32_32_32`
- `draw/intern/mesh_extractors/extract_mesh_vbo_skin_roots.cc`
  - Line 28: Update local_pos format
- `draw/intern/mesh_extractors/extract_mesh_vbo_lnor.cc`
- `draw/intern/mesh_extractors/extract_mesh_vbo_fdots_pos.cc`
- `draw/intern/mesh_extractors/extract_mesh_vbo_edituv_stretch_angle.cc`

**3.2 Draw Cache Implementations**
- `draw/intern/draw_cache_impl_curve.cc`
  - Lines 467, 550, 561, 672: Update pos attributes
- `draw/intern/draw_cache_impl_volume.cc`
  - Lines 159, 168, 251: Update pos_id formats
- `draw/intern/draw_cache_impl_curves.cc`
  - Lines 305, 1015: Update pos formats
- `draw/intern/draw_cache_impl_particles.cc`
- `draw/intern/draw_cache_impl_lattice.cc`
- `draw/intern/draw_cache_impl_grease_pencil.cc`

**3.3 PBVH & Rendering**
- `draw/intern/draw_pbvh.cc`
  - Line 285: Update vertex position format
- `draw/engines/eevee/eevee_lookdev.cc`
- `draw/engines/eevee/eevee_lightprobe_volume.cc`

#### Testing:
- Test mesh editing in 3D viewport
- Verify curve rendering
- Check sculpt mode functionality
- Validate grease pencil drawing

---

### Phase 4: Compositor & Rendering
**Duration:** 4-5 days

#### Tasks:

**4.1 Compositor**
- `compositor/intern/result.cc`
  - Lines 184, 201, 216, 245, 271, 574: Handle SFLOAT_32_32_32 → SFLOAT_32_32_32_32
  - Update `gpu_texture_format()` function logic
  - Modify result buffer allocation
- `compositor/cached_resources/intern/ocio_color_space_conversion_shader.cc`

**4.2 Render Results**
- `render/intern/render_result.cc`
  - Line 473: Update texture format selection logic
  - Ensure render passes use 4-component formats

**4.3 Color Management (OCIO)**
- `imbuf/opencolorio/intern/libocio/libocio_gpu_shader_binder.cc`
  - May require special handling for color space conversions
  - Ensure alpha channel doesn't affect color operations

#### Testing:
- Render test scenes
- Verify compositor nodes work correctly
- Check color management accuracy
- Test render passes (diffuse, specular, etc.)

---

### Phase 5: Editors & UI
**Duration:** 5-6 days

#### Tasks:

**5.1 3D Viewport**
- `editors/space_view3d/view3d_draw.cc`
- `editors/space_view3d/view3d_gizmo_*.cc` (ruler, navigate)
- `editors/space_view3d/view3d_placement.cc`
- `editors/space_view3d/view3d_cursor_snap.cc`

**5.2 Transform Tools**
- `editors/transform/transform_snap.cc`
- `editors/transform/transform_mode_vert_slide.cc`
- `editors/transform/transform_mode_edge_slide.cc`
- `editors/transform/transform_constraints.cc`

**5.3 Sculpt & Paint**
- `editors/sculpt_paint/paint_cursor.cc`
- `editors/sculpt_paint/curves_sculpt_ops.cc`
- `editors/sculpt_paint/sculpt_detail.cc`

**5.4 Gizmo Library**
- `editors/gizmo_library/gizmo_types/arrow3d_gizmo.cc`
- `editors/gizmo_library/gizmo_types/cage2d_gizmo.cc`
- `editors/gizmo_library/gizmo_types/cage3d_gizmo.cc`
- `editors/gizmo_library/gizmo_types/dial3d_gizmo.cc`
- `editors/gizmo_library/gizmo_types/move3d_gizmo.cc`
- `editors/gizmo_library/gizmo_types/primitive3d_gizmo.cc`
- `editors/gizmo_library/gizmo_types/button2d_gizmo.cc`
- `editors/gizmo_library/gizmo_draw_utils.cc`

**5.5 Other Editors**
- `editors/space_sequencer/sequencer_preview_draw.cc`
- `editors/space_node/node_draw.cc`
- `editors/space_file/file_draw.cc`
- `editors/space_clip/clip_draw.cc`
- `editors/screen/glutil.cc`
- `editors/screen/area.cc`
- `editors/interface/interface_widgets.cc`

**5.6 Grease Pencil**
- `editors/grease_pencil/intern/grease_pencil_primitive.cc`
- `editors/grease_pencil/intern/grease_pencil_image_render.cc`
- `editors/gpencil_legacy/annotate_draw.cc`

**5.7 Curves & Mesh Editing**
- `editors/curves/intern/curves_draw.cc`
- `editors/curve/editcurve_paint.cc`
- `editors/mesh/editmesh_preselect_*.cc` (edgering, elem)
- `editors/mesh/editmesh_knife.cc`
- `editors/object/object_remesh.cc`

#### Testing:
- Test all gizmo types (move, rotate, scale)
- Verify transform snapping
- Check sculpt cursor rendering
- Test grease pencil drawing
- Validate all editor viewports

---

### Phase 6: Python API & Other Systems
**Duration:** 2-3 days

#### Tasks:

**6.1 Python GPU Module**
- `python/gpu/gpu_py_texture.cc`
- `python/gpu/gpu_py_shader.cc`
- Update Python API documentation

**6.2 Window Manager**
- `windowmanager/intern/wm_playanim.cc`
- `windowmanager/intern/wm_draw.cc`
- `windowmanager/xr/intern/wm_xr_draw.cc`
- `windowmanager/xr/intern/wm_xr_operators.cc`

#### Testing:
- Run Python GPU API tests
- Verify XR rendering
- Test animation playback

---

### Phase 7: Format Removal & Cleanup
**Duration:** 2-3 days

#### Tasks:

**7.1 Remove Format Definitions**
- Delete format entries from `GPU_format.hh`
- Remove from `GPU_texture.hh` enums
- Update `to_data_format()` conversion function
- Clean up all TODO comments

**7.2 Update Tests**
- Update `gpu/tests/texture_test.cc`
- Update `gpu/vulkan/tests/vk_data_conversion_test.cc`
- Add tests for 4-component format correctness

**7.3 Documentation**
- Update GPU format documentation
- Document migration in developer handbook
- Add release notes entry

#### Testing:
- Full test suite run
- Verify no deprecated format references
- Check compilation on all platforms

---

### Phase 8: Final Validation
**Duration:** 3-4 days

#### Testing Checklist:

**Cross-Platform**
- [ ] Linux + OpenGL
- [ ] Linux + Vulkan
- [ ] macOS + Metal
- [ ] Windows + OpenGL
- [ ] Windows + Vulkan
- [ ] Windows + DirectX (if supported)

**Functional Tests**
- [ ] 3D viewport rendering
- [ ] Mesh editing (edit mode)
- [ ] Sculpt mode
- [ ] Grease Pencil
- [ ] Node editor
- [ ] Compositor
- [ ] Rendering (Cycles/EEVEE)
- [ ] Animation playback
- [ ] Transform gizmos
- [ ] All editor spaces

**Performance Tests**
- [ ] Viewport FPS (before/after)
- [ ] Render time (before/after)
- [ ] Memory usage
- [ ] GPU memory usage

**Regression Tests**
- [ ] Run full Blender test suite
- [ ] Check for visual regressions
- [ ] Verify no new crashes

---

## Risk Mitigation

### Potential Risks

1. **Visual Regressions**
   - **Risk:** Rendering artifacts from format conversion
   - **Mitigation:** Extensive visual testing, screenshot comparison

2. **Performance Impact**
   - **Risk:** 4-component formats use 33% more memory
   - **Mitigation:** Memory profiling, optimize buffer allocation

3. **Color Management Issues**
   - **Risk:** OCIO color conversions may be affected
   - **Mitigation:** Dedicated color accuracy testing

4. **Platform-Specific Bugs**
   - **Risk:** Different behavior on Metal/Vulkan/OpenGL
   - **Mitigation:** Test on all platforms before merge

### Rollback Plan

If critical issues arise:
1. Revert format enum changes
2. Restore 3-component format definitions
3. Re-enable emulation layer temporarily
4. Document blocking issues
5. Create targeted fix for specific problem

---

## Success Criteria

1. ✓ All 13 deprecated formats removed from codebase
2. ✓ All 75+ files successfully migrated
3. ✓ No compilation errors on any platform
4. ✓ Full test suite passes
5. ✓ No visual regressions
6. ✓ Performance within 5% of baseline
7. ✓ Code review approved
8. ✓ Documentation updated

---

## Timeline Summary

| Phase | Duration | Description |
|-------|----------|-------------|
| 1 | 3-4 days | Analysis & Preparation |
| 2 | 4-5 days | Core GPU Subsystem |
| 3 | 5-6 days | Draw System Migration |
| 4 | 4-5 days | Compositor & Rendering |
| 5 | 5-6 days | Editors & UI |
| 6 | 2-3 days | Python API & Other |
| 7 | 2-3 days | Format Removal & Cleanup |
| 8 | 3-4 days | Final Validation |
| **Total** | **28-36 days** | **~5-7 weeks** |

---

## Expected Benefits

### Technical Benefits
- Native Metal support without emulation
- 90%+ Vulkan device compatibility (vs <5%)
- Cleaner, more maintainable GPU codebase
- Future-proof for modern GPU APIs

### User Benefits
- Better macOS performance (Metal)
- Wider hardware compatibility (Vulkan)
- More stable rendering pipeline
- Foundation for future GPU features

### Project Benefits
- Removes 13 TODO items
- Reduces technical debt
- Improves code quality
- Aligns with industry standards

---

## References

- Issue: `GPU_texture.hh` lines 43, 48, 53, 58, 63, 68, 73, 78, 83, 88, 93, 98, 111
- Related: Pull request #114708 (Vulkan 3-component conversion)
- Vulkan docs: https://developer.blender.org/docs/features/gpu/vulkan/workarounds/
- Metal backend: https://code.blender.org/2023/01/introducing-the-blender-metal-viewport/

---

## Next Steps

To begin implementation:

1. **Start Phase 1:** Create detailed file audit and format conversion utilities
2. **Set up testing environment:** Ensure access to macOS (Metal) and Linux (Vulkan) systems
3. **Create feature branch:** `feature/remove-metal-incompatible-texture-formats`
4. **Engage with Blender developers:** Get feedback on migration approach

**Ready to proceed?**
