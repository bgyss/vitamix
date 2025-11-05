/* SPDX-FileCopyrightText: 2025 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup gpu
 *
 * Deprecation warnings for 3-component GPU texture formats.
 *
 * This header provides compile-time deprecation warnings for texture formats that are being
 * phased out due to poor hardware support on Metal and Vulkan backends.
 *
 * Usage:
 * - Define `GPU_ENABLE_FORMAT_DEPRECATION_WARNINGS` before including this header to enable
 *   deprecation warnings during compilation.
 * - Use this during migration to identify all code locations that need updating.
 * - Once migration is complete, the deprecated formats will be removed entirely.
 *
 * Example:
 * ```c
 * // In your source file that you're migrating:
 * #define GPU_ENABLE_FORMAT_DEPRECATION_WARNINGS
 * #include "GPU_format_deprecated.h"
 * ```
 *
 * This will emit compiler warnings like:
 * "warning: 'SFLOAT_32_32_32' is deprecated: Use SFLOAT_32_32_32_32 for Metal/Vulkan
 * compatibility"
 *
 * Migration Guide:
 * - SNORM_8_8_8       → SNORM_8_8_8_8
 * - SNORM_16_16_16    → SNORM_16_16_16_16
 * - UNORM_8_8_8       → UNORM_8_8_8_8
 * - UNORM_16_16_16    → UNORM_16_16_16_16
 * - SINT_8_8_8        → SINT_8_8_8_8
 * - SINT_16_16_16     → SINT_16_16_16_16
 * - SINT_32_32_32     → SINT_32_32_32_32
 * - UINT_8_8_8        → UINT_8_8_8_8
 * - UINT_16_16_16     → UINT_16_16_16_16
 * - UINT_32_32_32     → UINT_32_32_32_32
 * - SFLOAT_16_16_16   → SFLOAT_16_16_16_16
 * - SFLOAT_32_32_32   → SFLOAT_32_32_32_32
 * - SRGBA_8_8_8       → SRGBA_8_8_8_8
 */

#pragma once

/* Deprecation macros for 3-component texture formats.
 * These emit compile-time warnings to help track migration progress. */

#ifdef GPU_ENABLE_FORMAT_DEPRECATION_WARNINGS
#  if defined(__GNUC__) || defined(__clang__)
#    define GPU_FORMAT_DEPRECATED(msg) __attribute__((deprecated(msg)))
#  elif defined(_MSC_VER)
#    define GPU_FORMAT_DEPRECATED(msg) __declspec(deprecated(msg))
#  else
#    define GPU_FORMAT_DEPRECATED(msg) /* Deprecation not supported on this compiler */
#  endif
#else
#  define GPU_FORMAT_DEPRECATED(msg) /* Deprecation warnings disabled */
#endif

/* -------------------------------------------------------------------- */
/** \name Deprecation Warning Messages
 * \{ */

#define GPU_FORMAT_SNORM_8_8_8_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "SNORM_8_8_8 is deprecated. Use SNORM_8_8_8_8 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_SNORM_16_16_16_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "SNORM_16_16_16 is deprecated. Use SNORM_16_16_16_16 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_UNORM_8_8_8_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "UNORM_8_8_8 is deprecated. Use UNORM_8_8_8_8 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_UNORM_16_16_16_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "UNORM_16_16_16 is deprecated. Use UNORM_16_16_16_16 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_SINT_8_8_8_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "SINT_8_8_8 is deprecated. Use SINT_8_8_8_8 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_SINT_16_16_16_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "SINT_16_16_16 is deprecated. Use SINT_16_16_16_16 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_SINT_32_32_32_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "SINT_32_32_32 is deprecated. Use SINT_32_32_32_32 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_UINT_8_8_8_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "UINT_8_8_8 is deprecated. Use UINT_8_8_8_8 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_UINT_16_16_16_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "UINT_16_16_16 is deprecated. Use UINT_16_16_16_16 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_UINT_32_32_32_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "UINT_32_32_32 is deprecated. Use UINT_32_32_32_32 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_SFLOAT_16_16_16_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "SFLOAT_16_16_16 is deprecated. Use SFLOAT_16_16_16_16 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_SFLOAT_32_32_32_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "SFLOAT_32_32_32 is deprecated. Use SFLOAT_32_32_32_32 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

#define GPU_FORMAT_SRGBA_8_8_8_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "SRGBA_8_8_8 is deprecated. Use SRGBA_8_8_8_8 for Metal/Vulkan compatibility. " \
      "3-component formats have <5% hardware support.")

/** \} */

/* -------------------------------------------------------------------- */
/** \name Vertex Attribute Format Deprecation
 * \{ */

#define GPU_VERTEX_ATTR_SFLOAT_32_32_32_DEPRECATED \
  GPU_FORMAT_DEPRECATED( \
      "VertAttrType::SFLOAT_32_32_32 should be replaced with SFLOAT_32_32_32_32 " \
      "for better hardware compatibility. Consider using 4-component format.")

/** \} */

/* -------------------------------------------------------------------- */
/** \name Helper Functions for Migration
 * \{ */

#ifdef __cplusplus
namespace blender::gpu {

/**
 * Runtime warning for deprecated format usage.
 * Call this during initialization or first use of a deprecated format.
 */
inline void warn_deprecated_texture_format(const char *format_name,
                                            const char *location,
                                            const char *replacement)
{
  fprintf(stderr,
          "GPU Format Deprecation Warning: %s used at %s. "
          "Migrate to %s for Metal/Vulkan compatibility.\n",
          format_name,
          location,
          replacement);
}

/**
 * Helper to check if migration is needed at runtime.
 * Useful for conditional code during transition period.
 */
inline bool needs_format_migration()
{
  /* During migration, you can set this to return true to enable migration code paths */
  return true;
}

}  // namespace blender::gpu
#endif /* __cplusplus */

/** \} */

/* -------------------------------------------------------------------- */
/** \name Migration Status Tracking
 * \{ */

/**
 * Use these macros to mark files as migrated or still needing migration.
 * This helps track progress across the codebase.
 */
#define GPU_FORMAT_MIGRATION_TODO(subsystem) \
  _Pragma("message(\"TODO: Migrate " #subsystem " to 4-component GPU formats\")")

#define GPU_FORMAT_MIGRATION_IN_PROGRESS(subsystem) \
  _Pragma("message(\"IN PROGRESS: Migrating " #subsystem " to 4-component GPU formats\")")

#define GPU_FORMAT_MIGRATION_COMPLETE(subsystem) \
  _Pragma("message(\"COMPLETE: " #subsystem " migrated to 4-component GPU formats\")")

/** \} */

/* -------------------------------------------------------------------- */
/** \name Example Usage
 * \{ */

#if 0 /* Example code - do not compile */

/* Example 1: Enable deprecation warnings in a file you're migrating */
#define GPU_ENABLE_FORMAT_DEPRECATION_WARNINGS
#include "GPU_format_deprecated.h"

void my_function() {
  /* This will emit a deprecation warning: */
  TextureFormat format = TextureFormat::SFLOAT_32_32_32; /* deprecated! */

  /* Migrate to: */
  TextureFormat format = TextureFormat::SFLOAT_32_32_32_32; /* OK */
}

/* Example 2: Mark migration status */
GPU_FORMAT_MIGRATION_IN_PROGRESS(gizmo_library)

/* Example 3: Runtime warning for deprecated format */
if (is_deprecated_texture_format(format)) {
  warn_deprecated_texture_format(
    texture_format_to_string(format),
    __FILE__ ":" STRINGIFY(__LINE__),
    texture_format_to_string(to_compatible_texture_format(format))
  );
}

#endif /* Example code */

/** \} */
