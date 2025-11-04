# SPDX-FileCopyrightText: 2025 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Utility functions for LLM Prompting addon."""

import bpy
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


def log_info(message: str) -> None:
    """Log info message to console."""
    print(f"[LLM Prompting] INFO: {message}")


def log_error(message: str) -> None:
    """Log error message to console."""
    print(f"[LLM Prompting] ERROR: {message}")


def log_debug(message: str) -> None:
    """Log debug message to console."""
    print(f"[LLM Prompting] DEBUG: {message}")


def get_scene_context(context: bpy.types.Context) -> Dict[str, Any]:
    """
    Gather current scene context for LLM.

    Returns dictionary with scene information including:
    - Selected objects
    - Active object
    - Scene settings
    - Current mode
    """
    scene_info = {
        "mode": context.mode,
        "scene_name": context.scene.name,
        "frame_current": context.scene.frame_current,
        "objects_total": len(context.scene.objects),
    }

    # Selected objects
    selected = []
    if context.selected_objects:
        for obj in context.selected_objects:
            obj_info = {
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
                "rotation": list(obj.rotation_euler),
                "scale": list(obj.scale),
            }
            selected.append(obj_info)

    scene_info["selected_objects"] = selected

    # Active object
    if context.active_object:
        obj = context.active_object
        scene_info["active_object"] = {
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "vertex_count": len(obj.data.vertices) if hasattr(obj.data, 'vertices') else 0,
        }
    else:
        scene_info["active_object"] = None

    return scene_info


def get_scene_summary(context: bpy.types.Context) -> str:
    """
    Get human-readable scene summary for prompts.
    """
    scene = context.scene
    lines = [
        f"Scene: {scene.name}",
        f"Mode: {context.mode}",
        f"Frame: {scene.frame_current}",
        f"Total objects: {len(scene.objects)}",
    ]

    if context.selected_objects:
        lines.append(f"Selected: {len(context.selected_objects)} object(s)")
        for obj in context.selected_objects[:5]:  # Limit to first 5
            lines.append(f"  - {obj.name} ({obj.type})")
        if len(context.selected_objects) > 5:
            lines.append(f"  ... and {len(context.selected_objects) - 5} more")
    else:
        lines.append("No objects selected")

    if context.active_object:
        obj = context.active_object
        lines.append(f"Active object: {obj.name} ({obj.type})")

    return "\n".join(lines)


def format_timestamp() -> str:
    """Get current timestamp as string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_conversation_message(
    context: bpy.types.Context,
    role: str,
    content: str
) -> None:
    """
    Add message to conversation history.

    Args:
        context: Blender context
        role: Message role (user, assistant, system)
        content: Message content
    """
    props = context.scene.llm_prompting
    msg = props.conversation.add()
    msg.role = role
    msg.content = content
    msg.timestamp = format_timestamp()
    log_debug(f"Added message: {role}: {content[:50]}...")


def clear_conversation(context: bpy.types.Context) -> None:
    """Clear conversation history."""
    props = context.scene.llm_prompting
    props.conversation.clear()
    log_info("Conversation history cleared")


def get_conversation_history(
    context: bpy.types.Context,
    max_messages: Optional[int] = None
) -> List[Dict[str, str]]:
    """
    Get conversation history as list of dicts.

    Args:
        context: Blender context
        max_messages: Maximum number of recent messages to return

    Returns:
        List of {role, content} dictionaries
    """
    props = context.scene.llm_prompting
    messages = []

    conversation = props.conversation
    if max_messages:
        conversation = conversation[-max_messages:]

    for msg in conversation:
        messages.append({
            "role": msg.role,
            "content": msg.content,
        })

    return messages


def validate_code_safety(code: str) -> tuple[bool, Optional[str]]:
    """
    Validate if code is safe to execute.

    Returns:
        (is_safe, error_message)
    """
    # List of dangerous patterns
    dangerous_patterns = [
        'import os',
        'import sys',
        'import subprocess',
        'import shutil',
        '__import__',
        'exec(',
        'eval(',
        'compile(',
        'open(',
        'file(',
        'input(',
    ]

    code_lower = code.lower()

    for pattern in dangerous_patterns:
        if pattern in code_lower:
            return False, f"Dangerous pattern detected: {pattern}"

    return True, None


def sanitize_object_name(name: str) -> str:
    """Sanitize object name for safe use."""
    # Remove special characters, keep alphanumeric and basic punctuation
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"
    sanitized = ''.join(c if c in safe_chars else '_' for c in name)
    return sanitized[:63]  # Blender object name limit


def format_error_message(error: Exception) -> str:
    """Format exception as user-friendly message."""
    error_type = type(error).__name__
    error_msg = str(error)
    return f"{error_type}: {error_msg}"


def get_blender_version_info() -> Dict[str, Any]:
    """Get Blender version information."""
    return {
        "version": bpy.app.version_string,
        "version_tuple": bpy.app.version,
        "build_date": bpy.app.build_date.decode('utf-8') if isinstance(bpy.app.build_date, bytes) else bpy.app.build_date,
        "build_hash": bpy.app.build_hash.decode('utf-8') if isinstance(bpy.app.build_hash, bytes) else bpy.app.build_hash,
    }


def serialize_blender_data(data: Any) -> Any:
    """
    Serialize Blender data types to JSON-compatible format.

    Handles Vector, Matrix, Quaternion, etc.
    """
    import mathutils

    if isinstance(data, (mathutils.Vector, mathutils.Euler, mathutils.Color)):
        return list(data)
    elif isinstance(data, mathutils.Quaternion):
        return list(data)
    elif isinstance(data, mathutils.Matrix):
        return [list(row) for row in data]
    elif isinstance(data, (list, tuple)):
        return [serialize_blender_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: serialize_blender_data(value) for key, value in data.items()}
    else:
        return data


def parse_json_safely(json_str: str) -> Optional[Dict]:
    """
    Parse JSON string safely, returning None on error.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        log_error(f"JSON parse error: {e}")
        return None


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as JSON string."""
    return json.dumps(data, indent=indent, default=str)
