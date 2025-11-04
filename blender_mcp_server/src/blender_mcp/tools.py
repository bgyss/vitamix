# SPDX-FileCopyrightText: 2025 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tool definitions for Blender operations."""

from typing import Dict, Any
from .client import BlenderClient


# Tool schemas for Claude
BLENDER_TOOLS = [
    {
        "name": "create_cube",
        "description": "Create a cube in Blender",
        "input_schema": {
            "type": "object",
            "properties": {
                "size": {
                    "type": "number",
                    "description": "Size of the cube",
                    "default": 2.0
                },
                "location": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Location [x, y, z]",
                    "default": [0, 0, 0]
                }
            }
        }
    },
    {
        "name": "create_sphere",
        "description": "Create a sphere in Blender",
        "input_schema": {
            "type": "object",
            "properties": {
                "radius": {
                    "type": "number",
                    "description": "Radius of the sphere",
                    "default": 1.0
                },
                "location": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Location [x, y, z]",
                    "default": [0, 0, 0]
                },
                "segments": {
                    "type": "integer",
                    "description": "Number of segments",
                    "default": 32
                }
            }
        }
    },
    {
        "name": "create_cylinder",
        "description": "Create a cylinder in Blender",
        "input_schema": {
            "type": "object",
            "properties": {
                "radius": {
                    "type": "number",
                    "description": "Radius of the cylinder",
                    "default": 1.0
                },
                "depth": {
                    "type": "number",
                    "description": "Height/depth of the cylinder",
                    "default": 2.0
                },
                "location": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Location [x, y, z]",
                    "default": [0, 0, 0]
                }
            }
        }
    },
    {
        "name": "move_object",
        "description": "Move an object to a new location",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the object to move"
                },
                "location": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "New location [x, y, z]"
                }
            },
            "required": ["name", "location"]
        }
    },
    {
        "name": "scale_object",
        "description": "Scale an object",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the object to scale"
                },
                "scale": {
                    "description": "Scale factor (number for uniform, array [x,y,z] for non-uniform)",
                }
            },
            "required": ["name", "scale"]
        }
    },
    {
        "name": "rotate_object",
        "description": "Rotate an object",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the object to rotate"
                },
                "rotation": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Rotation in radians [x, y, z]"
                }
            },
            "required": ["name", "rotation"]
        }
    },
    {
        "name": "delete_object",
        "description": "Delete an object from the scene",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the object to delete"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "create_material",
        "description": "Create a new material",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the material"
                },
                "color": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "RGBA color [r, g, b, a] (values 0-1)",
                    "default": [0.8, 0.8, 0.8, 1.0]
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "assign_material",
        "description": "Assign a material to an object",
        "input_schema": {
            "type": "object",
            "properties": {
                "object_name": {
                    "type": "string",
                    "description": "Name of the object"
                },
                "material_name": {
                    "type": "string",
                    "description": "Name of the material"
                }
            },
            "required": ["object_name", "material_name"]
        }
    },
    {
        "name": "get_scene_info",
        "description": "Get information about the current scene",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "execute_python",
        "description": "Execute Python code in Blender (use with caution)",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If true, validate without executing",
                    "default": False
                }
            },
            "required": ["code"]
        }
    }
]


def execute_tool(client: BlenderClient, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool on Blender.

    Args:
        client: Blender client
        tool_name: Tool name
        tool_input: Tool input parameters

    Returns:
        Tool result dictionary
    """
    try:
        # Map tool names to operations
        if tool_name == "execute_python":
            # Special case: execute code
            return client.execute_code(
                code=tool_input["code"],
                dry_run=tool_input.get("dry_run", False)
            )
        elif tool_name == "get_scene_info":
            # Special case: get context
            return client.get_context()
        else:
            # Regular operation
            return client.execute_operation(tool_name, tool_input)

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
