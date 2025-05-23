# SPDX-FileCopyrightText: 2012 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

set(INC
  .
  ../../source/blender/gpu/intern
)

set(INC_SYS

)

set(SRC
  ocio_capi.cc
  fallback_impl.cc

  ocio_capi.h
  ocio_impl.h
  ocio_shader_shared.hh
)

set(LIB
  PRIVATE bf::blenlib
  PRIVATE bf::dna
  PRIVATE bf::gpu
  PRIVATE bf::intern::guardedalloc
  PRIVATE bf::intern::clog
)

if(WITH_OPENCOLORIO)
  add_definitions(
    -DWITH_OCIO
  )

  add_definitions(${OPENCOLORIO_DEFINITIONS})

  list(APPEND INC_SYS
    ${OPENCOLORIO_INCLUDE_DIRS}
    ${Epoxy_INCLUDE_DIRS}
  )

  list(APPEND SRC
    ocio_impl.cc
    ocio_impl_glsl.cc
  )

  list(APPEND LIB
    ${OPENCOLORIO_LIBRARIES}
  )

  set(GLSL_SRC
    gpu_shader_display_transform_vert.glsl
    gpu_shader_display_transform_frag.glsl

    ocio_shader_shared.hh
  )

  set(GLSL_C)
  foreach(GLSL_FILE ${GLSL_SRC})
    glsl_to_c(${GLSL_FILE} GLSL_C)
  endforeach()

  blender_add_lib(bf_ocio_shaders "${GLSL_C}" "" "" "")

  list(APPEND LIB
    bf_ocio_shaders
  )

  set(GLSL_SOURCE_CONTENT "")
  set(GLSL_METADATA_CONTENT "")
  foreach(GLSL_FILE ${GLSL_SRC})
    get_filename_component(GLSL_FILE_NAME ${GLSL_FILE} NAME)
    string(REPLACE "." "_" GLSL_FILE_NAME_UNDERSCORES ${GLSL_FILE_NAME})
    string(APPEND GLSL_SOURCE_CONTENT "SHADER_SOURCE\(${GLSL_FILE_NAME_UNDERSCORES}, \"${GLSL_FILE_NAME}\", \"${GLSL_FILE}\"\)\n")
    string(APPEND GLSL_METADATA_CONTENT "#include \"${GLSL_FILE}.hh\"\n")
  endforeach()

  set(glsl_source_list_file "${CMAKE_CURRENT_BINARY_DIR}/glsl_ocio_source_list.h")
  file(GENERATE OUTPUT ${glsl_source_list_file} CONTENT "${GLSL_SOURCE_CONTENT}")
  list(APPEND SRC ${glsl_source_list_file})
  set(glsl_metadata_list_file "${CMAKE_CURRENT_BINARY_DIR}/glsl_ocio_metadata_list.hh")
  file(GENERATE OUTPUT ${glsl_metadata_list_file} CONTENT "${GLSL_METADATA_CONTENT}")
  list(APPEND SRC ${glsl_metadata_list_file})
  list(APPEND INC ${CMAKE_CURRENT_BINARY_DIR})

  target_include_directories(bf_ocio_shaders PUBLIC ${CMAKE_CURRENT_BINARY_DIR})

endif()


blender_add_lib(bf_intern_opencolorio "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
