# SPDX-FileCopyrightText: 2025 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Property definitions for LLM Prompting addon."""

import bpy
from bpy.props import (
    StringProperty,
    IntProperty,
    FloatProperty,
    BoolProperty,
    EnumProperty,
    CollectionProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup


class LLMConversationMessage(PropertyGroup):
    """Individual message in conversation history."""

    role: StringProperty(
        name="Role",
        description="Message role (user, assistant, system)",
        default="user"
    )

    content: StringProperty(
        name="Content",
        description="Message content",
        default=""
    )

    timestamp: StringProperty(
        name="Timestamp",
        description="Message timestamp",
        default=""
    )


class LLMPromptingProperties(PropertyGroup):
    """Main properties for LLM Prompting system."""

    # Current prompt input
    prompt_input: StringProperty(
        name="Prompt",
        description="Enter your prompt for the LLM",
        default="",
        maxlen=4096
    )

    # Last response
    last_response: StringProperty(
        name="Last Response",
        description="Last response from LLM",
        default=""
    )

    # Conversation history
    conversation: CollectionProperty(
        type=LLMConversationMessage,
        name="Conversation History"
    )

    # Socket server settings
    server_enabled: BoolProperty(
        name="Server Enabled",
        description="Enable socket server for MCP communication",
        default=False
    )

    server_host: StringProperty(
        name="Server Host",
        description="Socket server host address",
        default="localhost"
    )

    server_port: IntProperty(
        name="Server Port",
        description="Socket server port",
        default=9876,
        min=1024,
        max=65535
    )

    # LLM settings
    model_provider: EnumProperty(
        name="Provider",
        description="LLM provider",
        items=[
            ('CLAUDE', "Claude (Anthropic)", "Use Claude AI models"),
            ('OPENAI', "OpenAI", "Use OpenAI GPT models"),
            ('LOCAL', "Local", "Use local models (Ollama, etc.)"),
        ],
        default='CLAUDE'
    )

    model_name: StringProperty(
        name="Model",
        description="Model name/identifier",
        default="claude-3-7-sonnet-20250219"
    )

    temperature: FloatProperty(
        name="Temperature",
        description="Sampling temperature (higher = more creative)",
        default=0.7,
        min=0.0,
        max=2.0
    )

    max_tokens: IntProperty(
        name="Max Tokens",
        description="Maximum tokens in response",
        default=4096,
        min=256,
        max=32000
    )

    # Execution settings
    auto_execute: BoolProperty(
        name="Auto Execute",
        description="Automatically execute LLM suggestions without preview",
        default=False
    )

    include_context: BoolProperty(
        name="Include Context",
        description="Include scene/selection context in prompts",
        default=True
    )

    include_screenshots: BoolProperty(
        name="Include Screenshots",
        description="Include viewport screenshots for vision models",
        default=False
    )

    # Status
    is_processing: BoolProperty(
        name="Processing",
        description="Currently processing a request",
        default=False
    )

    status_message: StringProperty(
        name="Status",
        description="Current status message",
        default=""
    )

    # Code preview
    preview_code: StringProperty(
        name="Preview Code",
        description="Generated code for preview",
        default=""
    )


class LLMPromptingPreferences(PropertyGroup):
    """Addon preferences for API keys and settings."""

    # API Keys (stored in preferences)
    claude_api_key: StringProperty(
        name="Claude API Key",
        description="Anthropic Claude API key",
        default="",
        subtype='PASSWORD'
    )

    openai_api_key: StringProperty(
        name="OpenAI API Key",
        description="OpenAI API key",
        default="",
        subtype='PASSWORD'
    )

    local_endpoint: StringProperty(
        name="Local Endpoint",
        description="Local model endpoint URL",
        default="http://localhost:11434"
    )

    # Security settings
    require_confirmation: BoolProperty(
        name="Require Confirmation",
        description="Require confirmation before executing code",
        default=True
    )

    enable_code_restrictions: BoolProperty(
        name="Enable Code Restrictions",
        description="Restrict dangerous operations in generated code",
        default=True
    )


# Registration
classes = (
    LLMConversationMessage,
    LLMPromptingProperties,
    LLMPromptingPreferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Add properties to Scene
    bpy.types.Scene.llm_prompting = PointerProperty(type=LLMPromptingProperties)

    # Add preferences to WindowManager (for easier access)
    bpy.types.WindowManager.llm_prompting_prefs = PointerProperty(type=LLMPromptingPreferences)


def unregister():
    # Remove properties
    del bpy.types.WindowManager.llm_prompting_prefs
    del bpy.types.Scene.llm_prompting

    # Unregister classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
