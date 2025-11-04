# SPDX-FileCopyrightText: 2025 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
LLM Prompting Addon for Blender

Provides integration with Large Language Models (LLMs) through Model Context Protocol (MCP).
Allows natural language control of Blender through AI assistants like Claude.

Features:
- Socket server for MCP communication
- Safe code execution
- Natural language prompts
- Scene context awareness
- Conversation history
- Multiple LLM provider support
"""

bl_info = {
    'name': 'LLM Prompting',
    'author': 'Blender Foundation',
    'version': (1, 0, 0),
    'blender': (4, 4, 0),
    'location': 'View3D > Sidebar > LLM Tab',
    'description': 'Control Blender with natural language through LLM integration (MCP)',
    'warning': 'Requires external MCP server for full functionality',
    'doc_url': '',
    'tracker_url': '',
    'support': 'COMMUNITY',
    'category': 'Interface',
}


# Check if running in Blender
if "bpy" in locals():
    # Reload modules for development
    import importlib
    if "properties" in locals():
        importlib.reload(properties)
    if "utils" in locals():
        importlib.reload(utils)
    if "socket_server" in locals():
        importlib.reload(socket_server)
    if "command_executor" in locals():
        importlib.reload(command_executor)
    if "operators" in locals():
        importlib.reload(operators)
    if "panels" in locals():
        importlib.reload(panels)


import bpy
from bpy.app.handlers import persistent

# Import addon modules
from . import properties
from . import utils
from . import socket_server
from . import command_executor
from . import operators
from . import panels


# Addon Preferences
class LLMPromptingAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    claude_api_key: bpy.props.StringProperty(
        name="Claude API Key",
        description="Anthropic Claude API key (optional - for direct integration)",
        default="",
        subtype='PASSWORD'
    )

    openai_api_key: bpy.props.StringProperty(
        name="OpenAI API Key",
        description="OpenAI API key (optional - for direct integration)",
        default="",
        subtype='PASSWORD'
    )

    local_endpoint: bpy.props.StringProperty(
        name="Local Model Endpoint",
        description="Local model endpoint URL (e.g., Ollama)",
        default="http://localhost:11434"
    )

    auto_start_server: bpy.props.BoolProperty(
        name="Auto-start Server",
        description="Automatically start socket server when Blender starts",
        default=False
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="MCP Socket Server", icon='NETWORK_DRIVE')
        box.prop(self, "auto_start_server")

        layout.separator()

        box = layout.box()
        box.label(text="API Keys (Optional)", icon='KEYINGSET')
        box.label(text="Required only for direct LLM integration", icon='INFO')

        box.prop(self, "claude_api_key")
        box.prop(self, "openai_api_key")

        layout.separator()

        box = layout.box()
        box.label(text="Local Models", icon='COMMUNITY')
        box.prop(self, "local_endpoint")

        layout.separator()

        box = layout.box()
        box.label(text="Quick Start:", icon='QUESTION')
        col = box.column(align=True)
        col.label(text="1. Enable this addon")
        col.label(text="2. Start socket server in LLM panel (View3D > Sidebar > LLM)")
        col.label(text="3. Run external MCP server (see documentation)")
        col.label(text="4. Connect via Claude Desktop or other MCP client")


# Load handler
@persistent
def load_handler(dummy):
    """Handler called when file is loaded."""
    # Auto-start server if enabled
    try:
        prefs = bpy.context.preferences.addons[__name__].preferences
        if prefs.auto_start_server:
            server = socket_server.get_server()
            if not server.is_running():
                props = bpy.context.scene.llm_prompting
                server.host = props.server_host
                server.port = props.server_port
                if server.start():
                    props.server_enabled = True
                    props.status_message = "Server auto-started"
                    utils.log_info("Socket server auto-started")
    except Exception as e:
        utils.log_error(f"Auto-start failed: {utils.format_error_message(e)}")


# Unload handler
def unload_handler():
    """Handler called when addon is disabled."""
    # Stop server
    server = socket_server.get_server()
    if server.is_running():
        server.stop()
        utils.log_info("Socket server stopped (addon unload)")


# Registration
def register():
    """Register addon classes and handlers."""
    utils.log_info(f"Registering LLM Prompting addon v{bl_info['version']}")

    # Register preferences first
    bpy.utils.register_class(LLMPromptingAddonPreferences)

    # Register modules
    properties.register()
    operators.register()
    panels.register()

    # Register handlers
    bpy.app.handlers.load_post.append(load_handler)

    utils.log_info("LLM Prompting addon registered successfully")


def unregister():
    """Unregister addon classes and handlers."""
    utils.log_info("Unregistering LLM Prompting addon")

    # Cleanup
    unload_handler()

    # Remove handlers
    if load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_handler)

    # Unregister modules (reverse order)
    panels.unregister()
    operators.unregister()
    properties.unregister()

    # Unregister preferences
    bpy.utils.unregister_class(LLMPromptingAddonPreferences)

    utils.log_info("LLM Prompting addon unregistered")


if __name__ == "__main__":
    register()
