# Phase 1: Comprehensive Format Usage Audit

**Date:** 2025-11-05
**Audit Scope:** All deprecated 3-component texture/vertex formats
**Total Files Analyzed:** 75+

---

## Executive Summary

This audit identifies all usages of 13 deprecated 3-component GPU formats across the Blender codebase.

### Key Findings:
- **94 unique usage locations** across 46 source files
- **Most common:** `SFLOAT_32_32_32` (vertex attributes: 58 uses, texture formats: 19 uses)
- **Second most common:** `SFLOAT_16_16_16` (texture formats: 16 uses)
- **Critical systems affected:** Editors (gizmos), Draw system, Vulkan backend, Compositor

---

## Deprecated Formats Usage Count

| Format | Texture Usage | Vertex Attr Usage | Total |
|--------|--------------|-------------------|-------|
| SFLOAT_32_32_32 | 19 | 58 | 77 |
| SFLOAT_16_16_16 | 16 | 0 | 16 |
| SNORM_8_8_8 | 7 | 0 | 7 |
| SNORM_16_16_16 | 7 | 0 | 7 |
| UNORM_8_8_8 | 7 | 0 | 7 |
| UNORM_16_16_16 | 7 | 0 | 7 |
| SINT_8_8_8 | 7 | 0 | 7 |
| SINT_16_16_16 | 7 | 0 | 7 |
| SINT_32_32_32 | 7 | 0 | 7 |
| UINT_8_8_8 | 8 | 0 | 8 |
| UINT_16_16_16 | 8 | 0 | 8 |
| UINT_32_32_32 | 7 | 0 | 7 |
| SRGBA_8_8_8 | 7 | 0 | 7 |
| **TOTAL** | **114** | **58** | **172** |

**Note:** Most Vulkan backend usages are in switch statements (format conversion handling)

---

## Category 1: Format Definitions (Critical - Must Update First)

### GPU_format.hh (13 format definitions)
**File:** `source/blender/gpu/GPU_format.hh`

```cpp
// Lines to modify:
Line 26:  SNORM_8_8_8_         // Remove or convert to SNORM_8_8_8_8_
Line 31:  SNORM_16_16_16_      // Remove or convert to SNORM_16_16_16_16_
Line 36:  UNORM_8_8_8_         // Remove or convert to UNORM_8_8_8_8_
Line 41:  UNORM_16_16_16_      // Remove or convert to UNORM_16_16_16_16_
Line 46:  SINT_8_8_8_          // Remove or convert to SINT_8_8_8_8_
Line 51:  SINT_16_16_16_       // Remove or convert to SINT_16_16_16_16_
Line 56:  SINT_32_32_32_       // Remove or convert to SINT_32_32_32_32_
Line 61:  UINT_8_8_8_          // Remove or convert to UINT_8_8_8_8_
Line 66:  UINT_16_16_16_       // Remove or convert to UINT_16_16_16_16_
Line 71:  UINT_32_32_32_       // Remove or convert to UINT_32_32_32_32_
Line 76:  SFLOAT_16_16_16_     // Remove or convert to SFLOAT_16_16_16_16_
Line 81:  SFLOAT_32_32_32_     // Remove or convert to SFLOAT_32_32_32_32_
Line 102: SRGBA_8_8_8_         // Remove or convert to SRGBA_8_8_8_8_
```

**Impact:** HIGH - Core format definitions, affects all other code
**Migration Strategy:** Add deprecation warnings first, then remove

---

## Category 2: Vulkan Backend (Format Conversion Layer)

### vk_data_conversion.cc (Major refactor needed)
**File:** `source/blender/gpu/vulkan/vk_data_conversion.cc`
**Total occurrences:** 77 (all 13 formats in multiple switch statements)

#### Function: `host_to_device_needs_conversion()`
- Lines 83, 88: SFLOAT format checks
- Lines 110, 120, 131, 149-150, 172-180: All 13 formats in switch cases

#### Function: `device_to_host_needs_conversion()`
- Lines 238-249, 260: All 13 formats in switch cases

#### Function: `to_component_len()`
- Lines 284, 323-333, 344: All 13 formats return 3 components

#### Function: `to_device_format()`
- Lines 398-409, 420: All 13 formats in switch cases

#### Function: `to_host_format_conversion()`
- Lines 477-488, 499: All 13 formats in switch cases

#### Function: `to_texture_format_vulkan()`
- Lines 524, 529, 536, 549-550, 572-580: All 13 formats in switch cases

**Impact:** CRITICAL - Core Vulkan conversion logic
**Migration Strategy:**
1. Update conversion functions to handle 4-component equivalents
2. Add automatic RGB→RGBA conversion layer
3. Test thoroughly on Vulkan devices

---

## Category 3: Editor Systems (High Volume)

### Gizmo Library (27 vertex attribute usages)

#### gizmo_types/dial3d_gizmo.cc
```cpp
Line 115:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
Line 195:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 225:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### gizmo_types/button2d_gizmo.cc
```cpp
Line 87:   uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
Line 180:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### gizmo_types/cage3d_gizmo.cc
```cpp
Line 128:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 176:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 211:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 253:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 307:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### gizmo_types/cage2d_gizmo.cc
```cpp
Line 93:   uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 379:  uint color = GPU_vertformat_attr_add(format, "color", SFLOAT_32_32_32);
Line 496:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 556:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### gizmo_types/arrow3d_gizmo.cc
```cpp
Line 84:   uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### gizmo_types/move3d_gizmo.cc
```cpp
Line 103:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
```

#### gizmo_types/primitive3d_gizmo.cc
```cpp
Line 115:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### gizmo_draw_utils.cc
```cpp
Line 26:   uint pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
```

**Impact:** HIGH - All gizmo rendering affected
**Migration:** Change SFLOAT_32_32_32 → SFLOAT_32_32_32_32 for all position/color attributes

---

### Transform System (8 usages)

#### transform_constraints.cc
```cpp
Line 756:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 812:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 885:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 920:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### transform_mode_vert_slide.cc
```cpp
Line 308:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### transform_mode_edge_slide.cc
```cpp
Line 475:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### transform_snap.cc
```cpp
Line 247:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 280:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

**Impact:** HIGH - Transform visualization affected
**Migration:** Change SFLOAT_32_32_32 → SFLOAT_32_32_32_32

---

### Space View3D (12 usages)

#### view3d_gizmo_navigate_type.cc
```cpp
Line 100:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
Line 180:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
Line 243:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
Line 302:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
```

#### view3d_gizmo_ruler.cc
```cpp
Line 262:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 315:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 362:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 404:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### view3d_cursor_snap.cc
```cpp
Line 171:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
Line 209:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### view3d_placement.cc
```cpp
Line 1070: uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### view3d_draw.cc
```cpp
Line 1743: uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

**Impact:** HIGH - 3D viewport visualization
**Migration:** Change SFLOAT_32_32_32 → SFLOAT_32_32_32_32

---

### Other Editors (9 usages)

#### space_sequencer/sequencer_preview_draw.cc
```cpp
Line 1416: uint col = GPU_vertformat_attr_add(format, "color", SFLOAT_32_32_32);
Line 1503: texture_format = gpu::TextureFormat::SFLOAT_32_32_32;  // TEXTURE FORMAT!
```

#### space_node/node_draw.cc
```cpp
Line 4307: uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### screen/glutil.cc (TEXTURE FORMATS!)
```cpp
Line 79:   TextureFormat::SFLOAT_16_16_16
Line 166:  ELEM(gpu_format, TextureFormat::SFLOAT_16_16_16)
Line 182:  TextureFormat::SFLOAT_16_16_16
Line 476:  format = TextureFormat::SFLOAT_16_16_16
```

#### screen/area.cc
```cpp
Line 4205: uint color = GPU_vertformat_attr_add(format, "color", SFLOAT_32_32_32);
```

#### interface/interface_widgets.cc
```cpp
Line 3120: uint color = GPU_vertformat_attr_add(format, "color", SFLOAT_32_32_32);
```

#### gpencil_legacy/annotate_draw.cc
```cpp
Line 269:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
Line 313:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
```

#### curves/intern/curves_draw.cc
```cpp
Line 408:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
```

#### object/object_remesh.cc
```cpp
Line 277:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### grease_pencil/intern/grease_pencil_image_render.cc
```cpp
Line 55:   uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
```

#### mesh/editmesh_knife.cc
```cpp
Line 395:  uint pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
```

#### mesh/editmesh_preselect_edgering.cc
```cpp
Line 53:   uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
```

#### mesh/editmesh_preselect_elem.cc
```cpp
Line 133:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
Line 158:  uint pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
Line 193:  uint pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
Line 264:  uint pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
```

#### curve/editcurve_paint.cc
```cpp
Line 231:  uint pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
```

#### sculpt_paint/paint_cursor.cc
```cpp
Line 1316: uint pos = GPU_vertformat_attr_add(imm->vertex_format, "pos", SFLOAT_32_32_32);
```

#### sculpt_paint/curves_sculpt_ops.cc
```cpp
Line 75:   uint pos = GPU_vertformat_attr_add(imm->vertex_format, "pos", SFLOAT_32_32_32);
```

#### sculpt_paint/sculpt_detail.cc
```cpp
Line 189:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
```

#### space_file/file_draw.cc
```cpp
Line 498:  uint pos = GPU_vertformat_attr_add(immVertexFormat(), "pos", SFLOAT_32_32_32);
```

#### space_clip/clip_draw.cc
```cpp
Line 1324: uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
```

**Impact:** MEDIUM-HIGH - Various editor visualizations
**Migration:** Change SFLOAT_32_32_32 → SFLOAT_32_32_32_32

---

## Category 4: Window Manager & XR (5 usages)

#### windowmanager/xr/intern/wm_xr_draw.cc
```cpp
Line 238:  GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
Line 239:  GPU_vertformat_attr_add(&format, "nor", SFLOAT_32_32_32);
Line 348:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
```

#### windowmanager/xr/intern/wm_xr_operators.cc
```cpp
Line 683:  uint pos = GPU_vertformat_attr_add(format, "pos", SFLOAT_32_32_32);
```

#### windowmanager/intern/wm_playanim.cc (TEXTURE FORMAT!)
```cpp
Line 539:  *r_format = blender::gpu::TextureFormat::SFLOAT_16_16_16;
```

#### windowmanager/intern/wm_draw.cc
```cpp
Line 289:  uint pos = GPU_vertformat_attr_add(imm_format, "pos", SFLOAT_32_32_32);
```

**Impact:** MEDIUM - XR rendering and animation playback
**Migration:** Update both vertex and texture formats

---

## Category 5: Rendering & Compositor (Critical)

### render/intern/render_result.cc (TEXTURE FORMAT!)
```cpp
Line 473:  format = use_half_float ? SFLOAT_16_16_16 : SFLOAT_32_32_32;
```

**Impact:** CRITICAL - Render output format selection
**Migration Strategy:**
- Change to SFLOAT_16_16_16_16 / SFLOAT_32_32_32_32
- Ensure render passes handle alpha channel correctly
- Test with all render engines (Cycles, EEVEE)

### compositor/intern/result.cc (5 texture format usages)
```cpp
Line 184:  case blender::gpu::TextureFormat::SFLOAT_32_32_32:
Line 201:  case blender::gpu::TextureFormat::SFLOAT_32_32_32:
Line 216:  return blender::gpu::TextureFormat::SFLOAT_32_32_32;
Line 245:  case blender::gpu::TextureFormat::SFLOAT_32_32_32:
Line 271:  case blender::gpu::TextureFormat::SFLOAT_32_32_32:
Line 574:  Result::gpu_texture_format(SFLOAT_32_32_32, ...);
```

**Impact:** CRITICAL - Compositor pipeline
**Migration Strategy:**
- Update all switch cases for SFLOAT_32_32_32 → SFLOAT_32_32_32_32
- Test compositor nodes thoroughly
- Verify color accuracy

---

## Category 6: Draw System (Mesh/Curve/Volume)

### draw/intern/draw_cache_impl_curve.cc (4 usages)
```cpp
Line 467:  attr_id.pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
Line 550:  attr_id.pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
Line 561:  attr_id.pos_hq = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
Line 672:  attr_id.pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
```

### draw/intern/draw_cache_impl_volume.cc (3 usages)
```cpp
Line 159:  attr_id.pos_id = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
Line 168:  pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
Line 251:  pos_id = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
```

### draw/intern/draw_cache_impl_curves.cc (2 usages)
```cpp
Line 305:  pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
Line 1015: pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
```

### draw/intern/draw_pbvh.cc (1 usage)
```cpp
Line 285:  pos = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
```

### draw/intern/mesh_extractors/extract_mesh_vbo_pos.cc (2 usages)
```cpp
Line 74:   pos_id = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
Line 136:  pos_id = GPU_vertformat_attr_add(&format, "pos", SFLOAT_32_32_32);
```

### draw/intern/mesh_extractors/extract_mesh_vbo_skin_roots.cc (1 usage)
```cpp
Line 28:   GPU_vertformat_attr_add(&format, "local_pos", SFLOAT_32_32_32);
```

### draw/intern/mesh_extractors/extract_mesh_vbo_lnor.cc
```cpp
Line 42:   lnor_id = GPU_vertformat_attr_add(&format, "nor", SFLOAT_32_32_32);
```

### draw/intern/mesh_extractors/extract_mesh_vbo_fdots_pos.cc
```cpp
Line 27:   fdots_pos_id = GPU_vertformat_attr_add(&format, "fdots_pos", SFLOAT_32_32_32);
```

### draw/intern/mesh_extractors/extract_mesh_vbo_edituv_stretch_angle.cc
```cpp
Line 32:   GPU_vertformat_attr_add(&format, "angle", SFLOAT_32_32_32);
```

### draw/intern/draw_cache_impl_particles.cc
```cpp
// Multiple position attribute usages
```

### draw/intern/draw_cache_impl_lattice.cc
```cpp
// Position attribute usages
```

### draw/intern/draw_cache_impl_grease_pencil.cc
```cpp
// Position attribute usages
```

**Impact:** CRITICAL - All mesh/curve/volume rendering
**Migration:** Update all position/normal/color attributes to 4-component

---

## Category 7: Python GPU API (2 usages)

### python/gpu/gpu_py_shader.cc
```cpp
Line 649:  GPU_vertformat_attr_add(&ret->fmt, "pos", SFLOAT_32_32_32);
```

### python/gpu/gpu_py_texture.cc (Texture format mapping!)
```cpp
Line 73:   {int(TextureFormat::SFLOAT_16_16_16), "RGB16F"},
```

**Impact:** MEDIUM - Python API compatibility
**Migration Strategy:**
- Update vertex format defaults
- Update texture format string mappings
- Add deprecation warnings to Python API
- Update Python API documentation

---

## Category 8: EEVEE/Overlay Engines

### draw/engines/eevee/eevee_lookdev.cc
```cpp
// Likely texture format usages (needs investigation)
```

### draw/engines/eevee/eevee_lightprobe_volume.cc
```cpp
// Likely texture format usages (needs investigation)
```

### draw/engines/overlay/overlay_motion_path.hh
```cpp
// Likely vertex format usages (needs investigation)
```

**Impact:** MEDIUM - EEVEE and overlay rendering
**Note:** These files need deeper investigation

---

## Migration Priority Order

### Phase 2A: Core GPU System (Week 1)
1. ✅ Add deprecation warnings to GPU_format.hh
2. ✅ Update format enum definitions
3. ✅ Update Vulkan conversion layer (vk_data_conversion.cc)
4. ✅ Run GPU tests

### Phase 2B: Critical Rendering (Week 2)
1. ✅ Update compositor/intern/result.cc (6 locations)
2. ✅ Update render/intern/render_result.cc (1 location)
3. ✅ Update screen/glutil.cc (4 texture format locations)
4. ✅ Test render output and compositor

### Phase 3A: Draw System Core (Week 3)
1. ✅ Update draw_cache_impl_*.cc files (15 locations)
2. ✅ Update mesh_extractors (9 locations)
3. ✅ Update draw_pbvh.cc (1 location)
4. ✅ Test mesh/curve/volume rendering

### Phase 3B: Editor Gizmos (Week 4)
1. ✅ Update all gizmo_types/*.cc files (27 locations)
2. ✅ Update gizmo_draw_utils.cc (1 location)
3. ✅ Test all gizmo types

### Phase 3C: Transform & View3D (Week 5)
1. ✅ Update transform_*.cc files (8 locations)
2. ✅ Update view3d_*.cc files (12 locations)
3. ✅ Test transform tools and 3D viewport

### Phase 4: Remaining Editors (Week 6)
1. ✅ Update space_* editor files (9 locations)
2. ✅ Update sculpt_paint, mesh, curve editors (15 locations)
3. ✅ Test all affected editors

### Phase 5: Window Manager & Python (Week 7)
1. ✅ Update windowmanager files (5 locations)
2. ✅ Update Python GPU API (2 locations)
3. ✅ Test XR rendering and Python scripts

### Phase 6: Format Removal (Week 8)
1. ✅ Remove format definitions from GPU_format.hh
2. ✅ Remove from GPU_texture.hh enums
3. ✅ Final testing and validation

---

## Testing Strategy

### Unit Tests
- [ ] Run `gpu/tests/texture_test.cc`
- [ ] Run `gpu/vulkan/tests/vk_data_conversion_test.cc`
- [ ] Verify format conversion correctness

### Integration Tests
- [ ] Test mesh rendering (edit mode, sculpt mode)
- [ ] Test curve/bezier rendering
- [ ] Test volume rendering
- [ ] Test compositor nodes
- [ ] Test render output (Cycles, EEVEE)
- [ ] Test all gizmo types
- [ ] Test transform tools (move, rotate, scale, constraints)
- [ ] Test grease pencil drawing
- [ ] Test XR rendering
- [ ] Test Python GPU scripts

### Visual Regression Tests
- [ ] Screenshot comparison for all major features
- [ ] Color accuracy verification
- [ ] Alpha channel handling verification

### Performance Tests
- [ ] Viewport FPS benchmark
- [ ] Render time benchmark
- [ ] Memory usage comparison

---

## Risk Assessment

### High Risk Areas
1. **Compositor (result.cc)** - Complex format conversion logic
2. **Render result (render_result.cc)** - Affects render output quality
3. **Vulkan backend (vk_data_conversion.cc)** - 77 locations to update
4. **Draw system** - Critical for all 3D viewport rendering

### Medium Risk Areas
1. **Gizmos** - Many locations but straightforward changes
2. **Transform system** - Affects user interaction
3. **Python API** - Compatibility concerns

### Low Risk Areas
1. **Individual editor visualizations** - Isolated changes
2. **XR system** - Less frequently used

---

## Success Criteria

- [ ] All 172 usages migrated to 4-component formats
- [ ] All 13 deprecated formats removed from GPU_format.hh
- [ ] Zero compilation errors
- [ ] All GPU tests pass
- [ ] No visual regressions
- [ ] Performance within 5% of baseline
- [ ] Python API backward compatibility maintained (with deprecation warnings)

---

## Next Steps

1. **Immediate:** Create format conversion utility functions
2. **Day 2:** Add compile-time deprecation warnings
3. **Day 3:** Establish GPU test baseline
4. **Day 4:** Begin Phase 2A (Core GPU System migration)

---

## File Summary

**Total files to modify:** 46
**Total code locations:** 172 (94 unique after grouping Vulkan switch cases)

### Files by subsystem:
- GPU Core: 2 files (GPU_format.hh, GPU_texture.hh)
- Vulkan: 1 file (vk_data_conversion.cc) - 77 locations
- Editors: 30 files
- Draw System: 12 files
- Rendering: 2 files (render_result.cc, result.cc)
- Window Manager: 3 files
- Python: 2 files

---

**Audit complete. Ready to proceed with Phase 1 implementation.**
