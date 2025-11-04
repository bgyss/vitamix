# SPDX-FileCopyrightText: 2025 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""UI Panels for LLM Prompting addon."""

import bpy
from bpy.types import Panel


class LLM_PT_main_panel(Panel):
    """Main LLM Prompting panel in 3D View"""
    bl_label = "LLM Prompting"
    bl_idname = "LLM_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LLM"

    def draw(self, context):
        layout = self.layout
        props = context.scene.llm_prompting

        # Header with status
        box = layout.box()
        row = box.row()
        row.label(text="Status:", icon='INFO')
        row = box.row()
        if props.server_enabled:
            row.label(text="Server Running", icon='CHECKMARK')
        else:
            row.label(text="Server Stopped", icon='X')

        if props.status_message:
            box.label(text=props.status_message, icon='DOT')

        layout.separator()

        # Server controls
        box = layout.box()
        box.label(text="Server Controls", icon='NETWORK_DRIVE')

        row = box.row()
        if props.server_enabled:
            row.operator("llm.toggle_server", text="Stop Server", icon='PAUSE')
        else:
            row.operator("llm.toggle_server", text="Start Server", icon='PLAY')

        row = box.row(align=True)
        row.prop(props, "server_host", text="Host")
        row.prop(props, "server_port", text="Port")

        row = box.row()
        row.operator("llm.test_connection", text="Test Connection", icon='PLUGIN')

        layout.separator()


class LLM_PT_prompt_panel(Panel):
    """Prompt input panel"""
    bl_label = "Prompt"
    bl_idname = "LLM_PT_prompt_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LLM"
    bl_parent_id = "LLM_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        props = context.scene.llm_prompting

        # Prompt input
        box = layout.box()
        box.label(text="Enter Prompt:", icon='CONSOLE')

        col = box.column(align=True)
        col.prop(props, "prompt_input", text="")

        row = box.row(align=True)
        row.operator("llm.execute_prompt", text="Send", icon='PLAY')
        row.operator("llm.add_context_to_prompt", text="Add Context", icon='PLUS')

        # Context settings
        row = box.row()
        row.prop(props, "include_context", text="Include Scene Context")


class LLM_PT_conversation_panel(Panel):
    """Conversation history panel"""
    bl_label = "Conversation"
    bl_idname = "LLM_PT_conversation_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LLM"
    bl_parent_id = "LLM_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        props = context.scene.llm_prompting

        # Conversation controls
        box = layout.box()
        row = box.row()
        row.label(text=f"Messages: {len(props.conversation)}", icon='WORDWRAP_ON')
        row.operator("llm.clear_conversation", text="", icon='TRASH')

        # Show last few messages
        if props.conversation:
            box.separator()

            # Show last 5 messages
            messages = list(props.conversation)[-5:]
            for msg in messages:
                msg_box = box.box()

                # Role header
                row = msg_box.row()
                if msg.role == "user":
                    row.label(text="You:", icon='USER')
                elif msg.role == "assistant":
                    row.label(text="Assistant:", icon='COMMUNITY')
                else:
                    row.label(text="System:", icon='INFO')

                row.label(text=msg.timestamp)

                # Message content (truncated)
                content = msg.content
                if len(content) > 200:
                    content = content[:200] + "..."

                col = msg_box.column(align=True)
                for line in content.split('\n')[:5]:  # Max 5 lines
                    if line:
                        col.label(text=line)

        # Last response
        if props.last_response:
            layout.separator()
            box = layout.box()
            box.label(text="Last Response:", icon='TEXT')

            response = props.last_response
            if len(response) > 300:
                response = response[:300] + "..."

            col = box.column(align=True)
            for line in response.split('\n')[:8]:  # Max 8 lines
                if line:
                    col.label(text=line)

            box.operator("llm.copy_response", text="Copy", icon='COPYDOWN')


class LLM_PT_code_preview_panel(Panel):
    """Code preview and execution panel"""
    bl_label = "Code Preview"
    bl_idname = "LLM_PT_code_preview_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LLM"
    bl_parent_id = "LLM_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        props = context.scene.llm_prompting

        box = layout.box()

        if props.preview_code:
            box.label(text="Generated Code:", icon='SCRIPTPLUGINS')

            # Show code preview (truncated)
            code = props.preview_code
            if len(code) > 400:
                code = code[:400] + "..."

            col = box.column(align=True)
            for line in code.split('\n')[:15]:  # Max 15 lines
                if line:
                    col.label(text=line, icon='BLANK1')

            box.separator()

            # Execution controls
            row = box.row(align=True)
            row.operator("llm.execute_code_preview", text="Execute", icon='PLAY')
            row.prop(props, "auto_execute", text="Auto")
        else:
            box.label(text="No code to preview", icon='INFO')


class LLM_PT_settings_panel(Panel):
    """Settings panel"""
    bl_label = "Settings"
    bl_idname = "LLM_PT_settings_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LLM"
    bl_parent_id = "LLM_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.llm_prompting
        prefs = context.window_manager.llm_prompting_prefs

        # LLM settings
        box = layout.box()
        box.label(text="LLM Settings", icon='PREFERENCES')

        box.prop(props, "model_provider", text="Provider")
        box.prop(props, "model_name", text="Model")
        box.prop(props, "temperature", text="Temperature")
        box.prop(props, "max_tokens", text="Max Tokens")

        layout.separator()

        # Security settings
        box = layout.box()
        box.label(text="Security", icon='LOCKED')

        box.prop(prefs, "require_confirmation", text="Require Confirmation")
        box.prop(prefs, "enable_code_restrictions", text="Code Restrictions")

        layout.separator()

        # API Keys (in preferences)
        box = layout.box()
        box.label(text="API Keys", icon='KEYINGSET')
        box.label(text="(Set in addon preferences)", icon='INFO')


class LLM_PT_help_panel(Panel):
    """Help panel"""
    bl_label = "Help"
    bl_idname = "LLM_PT_help_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LLM"
    bl_parent_id = "LLM_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Quick Start:", icon='QUESTION')

        col = box.column(align=True)
        col.label(text="1. Start the socket server")
        col.label(text="2. Run external MCP server")
        col.label(text="3. Connect via Claude/other client")
        col.label(text="4. Enter prompts to control Blender")

        layout.separator()

        box = layout.box()
        box.label(text="Operations:", icon='PROPERTIES')

        col = box.column(align=True)
        col.label(text="• Create/modify objects")
        col.label(text="• Apply materials")
        col.label(text="• Execute Python code")
        col.label(text="• Query scene information")

        layout.separator()

        box = layout.box()
        box.label(text="Server:", icon='NETWORK_DRIVE')
        col = box.column(align=True)
        col.label(text="Host: localhost (default)")
        col.label(text="Port: 9876 (default)")
        col.label(text="Protocol: JSON over TCP")


# List of panel classes for registration
classes = (
    LLM_PT_main_panel,
    LLM_PT_prompt_panel,
    LLM_PT_conversation_panel,
    LLM_PT_code_preview_panel,
    LLM_PT_settings_panel,
    LLM_PT_help_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
