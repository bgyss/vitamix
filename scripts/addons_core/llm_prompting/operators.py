# SPDX-FileCopyrightText: 2025 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Operators for LLM Prompting addon."""

import bpy
from bpy.types import Operator
from . import utils
from .socket_server import get_server
from .command_executor import get_executor


class LLM_OT_toggle_server(Operator):
    """Start or stop the MCP socket server"""
    bl_idname = "llm.toggle_server"
    bl_label = "Toggle Server"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.llm_prompting
        server = get_server()

        if server.is_running():
            # Stop server
            server.stop()
            props.server_enabled = False
            props.status_message = "Server stopped"
            self.report({'INFO'}, "Socket server stopped")
        else:
            # Start server
            server.host = props.server_host
            server.port = props.server_port

            # Set command handler
            def command_handler(message):
                return self._handle_command(message, context)

            server.set_command_handler(command_handler)

            if server.start():
                props.server_enabled = True
                props.status_message = f"Server running on {props.server_host}:{props.server_port}"
                self.report({'INFO'}, f"Socket server started on {props.server_host}:{props.server_port}")
            else:
                props.server_enabled = False
                props.status_message = "Failed to start server"
                self.report({'ERROR'}, "Failed to start socket server")

        return {'FINISHED'}

    def _handle_command(self, message, context):
        """Handle command from MCP client."""
        try:
            message_type = message.get('type', 'unknown')
            params = message.get('params', {})
            message_id = message.get('id')

            utils.log_debug(f"Handling command: {message_type}")

            executor = get_executor()

            if message_type == 'execute_operation':
                # Execute structured operation
                operation = params.get('operation')
                op_params = params.get('args', {})
                result = executor.execute_operation(operation, op_params, context)
                result['id'] = message_id
                return result

            elif message_type == 'execute_code':
                # Execute Python code
                code = params.get('code', '')
                dry_run = params.get('dry_run', False)
                result = executor.execute_code(code, context, dry_run)
                result['id'] = message_id
                return result

            elif message_type == 'get_context':
                # Get scene context
                context_data = utils.get_scene_context(context)
                return {
                    'status': 'success',
                    'result': context_data,
                    'id': message_id
                }

            elif message_type == 'ping':
                # Ping/health check
                return {
                    'status': 'success',
                    'message': 'pong',
                    'id': message_id
                }

            else:
                return {
                    'status': 'error',
                    'message': f'Unknown message type: {message_type}',
                    'id': message_id
                }

        except Exception as e:
            utils.log_error(f"Command handler error: {utils.format_error_message(e)}")
            return {
                'status': 'error',
                'message': utils.format_error_message(e),
                'id': message.get('id')
            }


class LLM_OT_execute_prompt(Operator):
    """Execute LLM prompt (placeholder - requires external MCP server)"""
    bl_idname = "llm.execute_prompt"
    bl_label = "Execute Prompt"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.llm_prompting
        prompt = props.prompt_input

        if not prompt:
            self.report({'WARNING'}, "No prompt entered")
            return {'CANCELLED'}

        # Add to conversation history
        utils.add_conversation_message(context, "user", prompt)

        # Check if server is running
        server = get_server()
        if not server.is_running():
            self.report({'WARNING'}, "Server not running. Start server first.")
            return {'CANCELLED'}

        # Note: Actual LLM interaction happens via external MCP server
        # This operator just adds the prompt to history
        # The MCP server will communicate back via socket

        props.status_message = "Prompt sent (MCP integration required)"
        props.prompt_input = ""  # Clear input

        self.report({'INFO'}, "Prompt sent to conversation")
        return {'FINISHED'}


class LLM_OT_execute_code_preview(Operator):
    """Execute code from preview"""
    bl_idname = "llm.execute_code_preview"
    bl_label = "Execute Code"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.llm_prompting
        code = props.preview_code

        if not code:
            self.report({'WARNING'}, "No code to execute")
            return {'CANCELLED'}

        executor = get_executor()
        result = executor.execute_code(code, context, dry_run=False)

        if result['status'] == 'success':
            self.report({'INFO'}, "Code executed successfully")
            utils.add_conversation_message(context, "system", "Code executed successfully")

            # Clear preview
            props.preview_code = ""

            return {'FINISHED'}
        else:
            error_msg = result.get('message', 'Unknown error')
            self.report({'ERROR'}, f"Execution failed: {error_msg}")
            utils.add_conversation_message(context, "system", f"Error: {error_msg}")
            return {'CANCELLED'}


class LLM_OT_clear_conversation(Operator):
    """Clear conversation history"""
    bl_idname = "llm.clear_conversation"
    bl_label = "Clear Conversation"
    bl_options = {'REGISTER'}

    def execute(self, context):
        utils.clear_conversation(context)
        props = context.scene.llm_prompting
        props.last_response = ""
        props.preview_code = ""
        props.status_message = "Conversation cleared"

        self.report({'INFO'}, "Conversation history cleared")
        return {'FINISHED'}


class LLM_OT_test_connection(Operator):
    """Test socket server connection"""
    bl_idname = "llm.test_connection"
    bl_label = "Test Connection"
    bl_options = {'REGISTER'}

    def execute(self, context):
        server = get_server()

        if not server.is_running():
            self.report({'WARNING'}, "Server not running")
            return {'CANCELLED'}

        # Server is running
        props = context.scene.llm_prompting
        self.report({'INFO'}, f"Server running on {props.server_host}:{props.server_port}")

        return {'FINISHED'}


class LLM_OT_add_context_to_prompt(Operator):
    """Add scene context to prompt input"""
    bl_idname = "llm.add_context_to_prompt"
    bl_label = "Add Context"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.llm_prompting

        # Get scene summary
        summary = utils.get_scene_summary(context)

        # Add to prompt
        if props.prompt_input:
            props.prompt_input += "\n\n"

        props.prompt_input += f"Current scene context:\n{summary}"

        self.report({'INFO'}, "Context added to prompt")
        return {'FINISHED'}


class LLM_OT_set_preview_code(Operator):
    """Set code for preview (called from external)"""
    bl_idname = "llm.set_preview_code"
    bl_label = "Set Preview Code"
    bl_options = {'REGISTER'}

    code: bpy.props.StringProperty(name="Code")

    def execute(self, context):
        props = context.scene.llm_prompting
        props.preview_code = self.code
        return {'FINISHED'}


class LLM_OT_copy_response(Operator):
    """Copy last response to clipboard"""
    bl_idname = "llm.copy_response"
    bl_label = "Copy Response"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.llm_prompting
        response = props.last_response

        if not response:
            self.report({'WARNING'}, "No response to copy")
            return {'CANCELLED'}

        context.window_manager.clipboard = response
        self.report({'INFO'}, "Response copied to clipboard")

        return {'FINISHED'}


# List of operator classes for registration
classes = (
    LLM_OT_toggle_server,
    LLM_OT_execute_prompt,
    LLM_OT_execute_code_preview,
    LLM_OT_clear_conversation,
    LLM_OT_test_connection,
    LLM_OT_add_context_to_prompt,
    LLM_OT_set_preview_code,
    LLM_OT_copy_response,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
