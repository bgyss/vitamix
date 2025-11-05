/* SPDX-FileCopyrightText: 2025 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup gpu
 *
 * GPU format conversion utilities for migrating from 3-component to 4-component formats.
 *
 * This file provides helper functions to convert deprecated 3-component (RGB) texture and
 * vertex formats to their 4-component (RGBA) equivalents. This migration is necessary for
 * improved compatibility with Metal (macOS), Vulkan, and other modern GPU APIs.
 *
 * Background:
 * - 3-component formats have <5% hardware support on Vulkan
 * - 4-component formats have >90% hardware support
 * - Metal backend requires format emulation for 3-component formats
 * - This adds overhead and compatibility issues
 *
 * Usage:
 * - Use `to_compatible_texture_format()` to convert TextureFormat
 * - Use `to_compatible_vertex_attr_type()` to convert VertAttrType
 * - Use `is_deprecated_format()` to check if a format is deprecated
 */

#pragma once

#include "GPU_format.hh"
#include "GPU_texture.hh"

namespace blender::gpu {

/* -------------------------------------------------------------------- */
/** \name Deprecated Format Detection
 * \{ */

/**
 * Check if a TextureFormat is deprecated (3-component format).
 * Returns true for formats that should be migrated to 4-component equivalents.
 */
constexpr bool is_deprecated_texture_format(TextureFormat format)
{
  switch (format) {
    case TextureFormat::SNORM_8_8_8:
    case TextureFormat::SNORM_16_16_16:
    case TextureFormat::UNORM_8_8_8:
    case TextureFormat::UNORM_16_16_16:
    case TextureFormat::SINT_8_8_8:
    case TextureFormat::SINT_16_16_16:
    case TextureFormat::SINT_32_32_32:
    case TextureFormat::UINT_8_8_8:
    case TextureFormat::UINT_16_16_16:
    case TextureFormat::UINT_32_32_32:
    case TextureFormat::SFLOAT_16_16_16:
    case TextureFormat::SFLOAT_32_32_32:
    case TextureFormat::SRGBA_8_8_8:
      return true;
    default:
      return false;
  }
}

/**
 * Check if a VertAttrType is deprecated (3-component format).
 * Currently only SFLOAT_32_32_32 vertex attributes are widely used.
 */
constexpr bool is_deprecated_vertex_attr_type(VertAttrType type)
{
  /* Note: Only vertex attribute types that are actually deprecated should be listed here.
   * Currently, 3-component vertex formats are being phased out in favor of 4-component. */
  return false; /* Vertex attributes don't have the same deprecation as textures */
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Format Conversion Functions
 * \{ */

/**
 * Convert deprecated 3-component TextureFormat to 4-component equivalent.
 * If the format is not deprecated, returns the original format unchanged.
 */
constexpr TextureFormat to_compatible_texture_format(TextureFormat format)
{
  switch (format) {
    case TextureFormat::SNORM_8_8_8:
      return TextureFormat::SNORM_8_8_8_8;
    case TextureFormat::SNORM_16_16_16:
      return TextureFormat::SNORM_16_16_16_16;
    case TextureFormat::UNORM_8_8_8:
      return TextureFormat::UNORM_8_8_8_8;
    case TextureFormat::UNORM_16_16_16:
      return TextureFormat::UNORM_16_16_16_16;
    case TextureFormat::SINT_8_8_8:
      return TextureFormat::SINT_8_8_8_8;
    case TextureFormat::SINT_16_16_16:
      return TextureFormat::SINT_16_16_16_16;
    case TextureFormat::SINT_32_32_32:
      return TextureFormat::SINT_32_32_32_32;
    case TextureFormat::UINT_8_8_8:
      return TextureFormat::UINT_8_8_8_8;
    case TextureFormat::UINT_16_16_16:
      return TextureFormat::UINT_16_16_16_16;
    case TextureFormat::UINT_32_32_32:
      return TextureFormat::UINT_32_32_32_32;
    case TextureFormat::SFLOAT_16_16_16:
      return TextureFormat::SFLOAT_16_16_16_16;
    case TextureFormat::SFLOAT_32_32_32:
      return TextureFormat::SFLOAT_32_32_32_32;
    case TextureFormat::SRGBA_8_8_8:
      return TextureFormat::SRGBA_8_8_8_8;
    default:
      /* Format is not deprecated or already 4-component */
      return format;
  }
}

/**
 * Convert 3-component VertAttrType to 4-component equivalent for position/normal/color data.
 * This is primarily for SFLOAT_32_32_32 which is the most commonly used 3-component vertex format.
 *
 * Note: The actual VertAttrType enum may not have deprecated 3-component types marked,
 * but this function provides a migration path for code that should use 4-component formats.
 */
constexpr VertAttrType to_compatible_vertex_attr_type(VertAttrType type)
{
  /* Most vertex attribute types don't need conversion, but this provides a future-proof
   * API for any conversions that might be needed. Currently returns the input unchanged. */
  return type;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Component Count Utilities
 * \{ */

/**
 * Get the number of components in a TextureFormat.
 * Returns 3 for deprecated formats, 4 for their replacements.
 */
constexpr int texture_format_component_count(TextureFormat format)
{
  switch (format) {
    case TextureFormat::SNORM_8_8_8:
    case TextureFormat::SNORM_16_16_16:
    case TextureFormat::UNORM_8_8_8:
    case TextureFormat::UNORM_16_16_16:
    case TextureFormat::SINT_8_8_8:
    case TextureFormat::SINT_16_16_16:
    case TextureFormat::SINT_32_32_32:
    case TextureFormat::UINT_8_8_8:
    case TextureFormat::UINT_16_16_16:
    case TextureFormat::UINT_32_32_32:
    case TextureFormat::SFLOAT_16_16_16:
    case TextureFormat::SFLOAT_32_32_32:
    case TextureFormat::SRGBA_8_8_8:
      return 3;

    case TextureFormat::SNORM_8_8_8_8:
    case TextureFormat::SNORM_16_16_16_16:
    case TextureFormat::UNORM_8_8_8_8:
    case TextureFormat::UNORM_16_16_16_16:
    case TextureFormat::SINT_8_8_8_8:
    case TextureFormat::SINT_16_16_16_16:
    case TextureFormat::SINT_32_32_32_32:
    case TextureFormat::UINT_8_8_8_8:
    case TextureFormat::UINT_16_16_16_16:
    case TextureFormat::UINT_32_32_32_32:
    case TextureFormat::SFLOAT_16_16_16_16:
    case TextureFormat::SFLOAT_32_32_32_32:
    case TextureFormat::SRGBA_8_8_8_8:
      return 4;

    default:
      return 0; /* Unknown or special format */
  }
}

/**
 * Check if a format pair represents the same data with different component counts.
 * Used to verify that format conversions are semantically equivalent.
 */
constexpr bool are_equivalent_formats(TextureFormat format_rgb, TextureFormat format_rgba)
{
  return to_compatible_texture_format(format_rgb) == format_rgba;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Migration Helper Macros
 * \{ */

/**
 * Emit a deprecation warning for 3-component texture formats.
 * Use this in code that still uses deprecated formats during migration.
 */
#define GPU_TEXTURE_FORMAT_DEPRECATED(format) \
  static_assert(::blender::gpu::is_deprecated_texture_format(format), \
                "This format is deprecated. Use to_compatible_texture_format() to convert to " \
                "4-component equivalent for Metal/Vulkan compatibility.")

/**
 * Helper macro to convert and warn about deprecated texture format usage.
 * Use during migration to make deprecated format usage visible.
 */
#define GPU_TEXTURE_FORMAT_COMPAT(format) \
  (::blender::gpu::is_deprecated_texture_format(format) ? \
   ::blender::gpu::to_compatible_texture_format(format) : \
   (format))

/** \} */

/* -------------------------------------------------------------------- */
/** \name Format String Utilities (for debugging/logging)
 * \{ */

/**
 * Get a human-readable string name for a TextureFormat.
 * Useful for logging deprecation warnings and migration progress.
 */
constexpr const char *texture_format_to_string(TextureFormat format)
{
  switch (format) {
    case TextureFormat::SNORM_8_8_8: return "SNORM_8_8_8 (deprecated)";
    case TextureFormat::SNORM_16_16_16: return "SNORM_16_16_16 (deprecated)";
    case TextureFormat::UNORM_8_8_8: return "UNORM_8_8_8 (deprecated)";
    case TextureFormat::UNORM_16_16_16: return "UNORM_16_16_16 (deprecated)";
    case TextureFormat::SINT_8_8_8: return "SINT_8_8_8 (deprecated)";
    case TextureFormat::SINT_16_16_16: return "SINT_16_16_16 (deprecated)";
    case TextureFormat::SINT_32_32_32: return "SINT_32_32_32 (deprecated)";
    case TextureFormat::UINT_8_8_8: return "UINT_8_8_8 (deprecated)";
    case TextureFormat::UINT_16_16_16: return "UINT_16_16_16 (deprecated)";
    case TextureFormat::UINT_32_32_32: return "UINT_32_32_32 (deprecated)";
    case TextureFormat::SFLOAT_16_16_16: return "SFLOAT_16_16_16 (deprecated)";
    case TextureFormat::SFLOAT_32_32_32: return "SFLOAT_32_32_32 (deprecated)";
    case TextureFormat::SRGBA_8_8_8: return "SRGBA_8_8_8 (deprecated)";

    case TextureFormat::SNORM_8_8_8_8: return "SNORM_8_8_8_8";
    case TextureFormat::SNORM_16_16_16_16: return "SNORM_16_16_16_16";
    case TextureFormat::UNORM_8_8_8_8: return "UNORM_8_8_8_8";
    case TextureFormat::UNORM_16_16_16_16: return "UNORM_16_16_16_16";
    case TextureFormat::SINT_8_8_8_8: return "SINT_8_8_8_8";
    case TextureFormat::SINT_16_16_16_16: return "SINT_16_16_16_16";
    case TextureFormat::SINT_32_32_32_32: return "SINT_32_32_32_32";
    case TextureFormat::UINT_8_8_8_8: return "UINT_8_8_8_8";
    case TextureFormat::UINT_16_16_16_16: return "UINT_16_16_16_16";
    case TextureFormat::UINT_32_32_32_32: return "UINT_32_32_32_32";
    case TextureFormat::SFLOAT_16_16_16_16: return "SFLOAT_16_16_16_16";
    case TextureFormat::SFLOAT_32_32_32_32: return "SFLOAT_32_32_32_32";
    case TextureFormat::SRGBA_8_8_8_8: return "SRGBA_8_8_8_8";

    default: return "Unknown format";
  }
}

/**
 * Get migration suggestion string for a deprecated format.
 */
constexpr const char *texture_format_migration_hint(TextureFormat format)
{
  if (!is_deprecated_texture_format(format)) {
    return "No migration needed - format is already compatible.";
  }

  switch (format) {
    case TextureFormat::SNORM_8_8_8:
      return "Migrate to SNORM_8_8_8_8 for Metal/Vulkan compatibility.";
    case TextureFormat::SNORM_16_16_16:
      return "Migrate to SNORM_16_16_16_16 for Metal/Vulkan compatibility.";
    case TextureFormat::UNORM_8_8_8:
      return "Migrate to UNORM_8_8_8_8 for Metal/Vulkan compatibility.";
    case TextureFormat::UNORM_16_16_16:
      return "Migrate to UNORM_16_16_16_16 for Metal/Vulkan compatibility.";
    case TextureFormat::SINT_8_8_8:
      return "Migrate to SINT_8_8_8_8 for Metal/Vulkan compatibility.";
    case TextureFormat::SINT_16_16_16:
      return "Migrate to SINT_16_16_16_16 for Metal/Vulkan compatibility.";
    case TextureFormat::SINT_32_32_32:
      return "Migrate to SINT_32_32_32_32 for Metal/Vulkan compatibility.";
    case TextureFormat::UINT_8_8_8:
      return "Migrate to UINT_8_8_8_8 for Metal/Vulkan compatibility.";
    case TextureFormat::UINT_16_16_16:
      return "Migrate to UINT_16_16_16_16 for Metal/Vulkan compatibility.";
    case TextureFormat::UINT_32_32_32:
      return "Migrate to UINT_32_32_32_32 for Metal/Vulkan compatibility.";
    case TextureFormat::SFLOAT_16_16_16:
      return "Migrate to SFLOAT_16_16_16_16 for Metal/Vulkan compatibility.";
    case TextureFormat::SFLOAT_32_32_32:
      return "Migrate to SFLOAT_32_32_32_32 for Metal/Vulkan compatibility.";
    case TextureFormat::SRGBA_8_8_8:
      return "Migrate to SRGBA_8_8_8_8 for Metal/Vulkan compatibility.";
    default:
      return "Unknown format - check GPU_format_conversion.hh";
  }
}

/** \} */

}  // namespace blender::gpu
