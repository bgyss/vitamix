# SPDX-FileCopyrightText: 2025 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Command executor for safe execution of LLM-generated code."""

import bpy
import math
import mathutils
from typing import Dict, Any, Optional
from . import utils


class CommandExecutor:
    """Executes LLM-generated commands and code safely."""

    def __init__(self):
        self.last_error = None
        self.last_result = None

    def execute_operation(
        self,
        operation: str,
        params: Dict[str, Any],
        context: bpy.types.Context
    ) -> Dict[str, Any]:
        """
        Execute a structured operation.

        Args:
            operation: Operation name (e.g., 'create_cube')
            params: Operation parameters
            context: Blender context

        Returns:
            Result dictionary with status and data
        """
        utils.log_debug(f"Executing operation: {operation}")

        try:
            # Dispatch to appropriate handler
            handler_name = f"_op_{operation}"
            if hasattr(self, handler_name):
                handler = getattr(self, handler_name)
                result = handler(params, context)
                self.last_result = result
                return {
                    "status": "success",
                    "result": result
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unknown operation: {operation}"
                }

        except Exception as e:
            self.last_error = e
            utils.log_error(f"Operation failed: {utils.format_error_message(e)}")
            return {
                "status": "error",
                "message": utils.format_error_message(e)
            }

    def execute_code(
        self,
        code: str,
        context: bpy.types.Context,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute arbitrary Python code safely.

        Args:
            code: Python code to execute
            context: Blender context
            dry_run: If True, validate without executing

        Returns:
            Result dictionary with status and data
        """
        utils.log_debug(f"Executing code (dry_run={dry_run})")

        # Validate code safety
        is_safe, error_msg = utils.validate_code_safety(code)
        if not is_safe:
            return {
                "status": "error",
                "message": f"Code safety check failed: {error_msg}"
            }

        if dry_run:
            return {
                "status": "success",
                "message": "Code validation passed",
                "code": code
            }

        # Create restricted execution environment
        restricted_globals = self._create_restricted_globals(context)

        try:
            # Execute code
            exec(code, restricted_globals)

            self.last_result = {
                "executed": True,
                "code_length": len(code)
            }

            return {
                "status": "success",
                "message": "Code executed successfully",
                "result": self.last_result
            }

        except Exception as e:
            self.last_error = e
            utils.log_error(f"Code execution failed: {utils.format_error_message(e)}")
            return {
                "status": "error",
                "message": utils.format_error_message(e)
            }

    def _create_restricted_globals(self, context: bpy.types.Context) -> Dict[str, Any]:
        """
        Create restricted globals dictionary for safe code execution.
        """
        # Allowed built-in functions
        safe_builtins = {
            'range': range,
            'len': len,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'round': round,
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sorted': sorted,
            'reversed': reversed,
            'print': print,
        }

        return {
            '__builtins__': safe_builtins,
            'bpy': bpy,
            'math': math,
            'mathutils': mathutils,
            'C': context,
            'context': context,
            'D': bpy.data,
            'data': bpy.data,
        }

    # Operation handlers

    def _op_create_cube(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Create a cube."""
        size = params.get('size', 2.0)
        location = params.get('location', (0, 0, 0))

        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        obj = context.active_object

        return {
            "object_name": obj.name,
            "type": "MESH"
        }

    def _op_create_sphere(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Create a sphere."""
        radius = params.get('radius', 1.0)
        location = params.get('location', (0, 0, 0))
        segments = params.get('segments', 32)

        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=radius,
            location=location,
            segments=segments,
            ring_count=segments // 2
        )
        obj = context.active_object

        return {
            "object_name": obj.name,
            "type": "MESH"
        }

    def _op_create_cylinder(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Create a cylinder."""
        radius = params.get('radius', 1.0)
        depth = params.get('depth', 2.0)
        location = params.get('location', (0, 0, 0))

        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius,
            depth=depth,
            location=location
        )
        obj = context.active_object

        return {
            "object_name": obj.name,
            "type": "MESH"
        }

    def _op_create_plane(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Create a plane."""
        size = params.get('size', 2.0)
        location = params.get('location', (0, 0, 0))

        bpy.ops.mesh.primitive_plane_add(size=size, location=location)
        obj = context.active_object

        return {
            "object_name": obj.name,
            "type": "MESH"
        }

    def _op_delete_object(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Delete an object by name."""
        name = params.get('name')

        if not name:
            raise ValueError("Object name required")

        obj = bpy.data.objects.get(name)
        if not obj:
            raise ValueError(f"Object '{name}' not found")

        bpy.data.objects.remove(obj, do_unlink=True)

        return {
            "deleted": name
        }

    def _op_move_object(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Move an object."""
        name = params.get('name')
        location = params.get('location')

        if not name:
            raise ValueError("Object name required")
        if not location:
            raise ValueError("Location required")

        obj = bpy.data.objects.get(name)
        if not obj:
            raise ValueError(f"Object '{name}' not found")

        obj.location = location

        return {
            "object_name": name,
            "new_location": list(obj.location)
        }

    def _op_scale_object(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Scale an object."""
        name = params.get('name')
        scale = params.get('scale')

        if not name:
            raise ValueError("Object name required")
        if not scale:
            raise ValueError("Scale required")

        obj = bpy.data.objects.get(name)
        if not obj:
            raise ValueError(f"Object '{name}' not found")

        # Scale can be single value or tuple
        if isinstance(scale, (int, float)):
            obj.scale = (scale, scale, scale)
        else:
            obj.scale = scale

        return {
            "object_name": name,
            "new_scale": list(obj.scale)
        }

    def _op_rotate_object(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Rotate an object."""
        name = params.get('name')
        rotation = params.get('rotation')

        if not name:
            raise ValueError("Object name required")
        if not rotation:
            raise ValueError("Rotation required")

        obj = bpy.data.objects.get(name)
        if not obj:
            raise ValueError(f"Object '{name}' not found")

        obj.rotation_euler = rotation

        return {
            "object_name": name,
            "new_rotation": list(obj.rotation_euler)
        }

    def _op_create_material(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Create a material."""
        name = params.get('name', 'Material')
        color = params.get('color', (0.8, 0.8, 0.8, 1.0))

        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True

        # Set base color
        if mat.node_tree:
            nodes = mat.node_tree.nodes
            principled = nodes.get('Principled BSDF')
            if principled:
                principled.inputs['Base Color'].default_value = color

        return {
            "material_name": mat.name,
            "color": color
        }

    def _op_assign_material(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Assign material to object."""
        object_name = params.get('object_name')
        material_name = params.get('material_name')

        if not object_name:
            raise ValueError("Object name required")
        if not material_name:
            raise ValueError("Material name required")

        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")

        mat = bpy.data.materials.get(material_name)
        if not mat:
            raise ValueError(f"Material '{material_name}' not found")

        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        return {
            "object_name": object_name,
            "material_name": material_name
        }

    def _op_get_scene_info(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Get scene information."""
        return utils.get_scene_context(context)

    def _op_select_object(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Select an object by name."""
        name = params.get('name')

        if not name:
            raise ValueError("Object name required")

        obj = bpy.data.objects.get(name)
        if not obj:
            raise ValueError(f"Object '{name}' not found")

        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')

        # Select object
        obj.select_set(True)
        context.view_layer.objects.active = obj

        return {
            "selected": name
        }

    def _op_render_image(self, params: Dict[str, Any], context: bpy.types.Context) -> Dict[str, Any]:
        """Render current view."""
        filepath = params.get('filepath', '/tmp/render.png')

        bpy.ops.render.render(write_still=True)

        scene = context.scene
        scene.render.filepath = filepath

        return {
            "filepath": filepath,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y]
        }


# Global executor instance
_executor = None


def get_executor() -> CommandExecutor:
    """Get global command executor instance."""
    global _executor
    if _executor is None:
        _executor = CommandExecutor()
    return _executor
