# SPDX-FileCopyrightText: 2025 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""MCP Server for Blender integration."""

import os
import sys
import json
import asyncio
from typing import Any, Dict, Optional
from anthropic import Anthropic

from .client import BlenderClient
from .tools import BLENDER_TOOLS, execute_tool


class BlenderMCPServer:
    """MCP Server that bridges LLM and Blender."""

    def __init__(
        self,
        blender_host: str = "localhost",
        blender_port: int = 9876,
        api_key: Optional[str] = None
    ):
        """
        Initialize MCP server.

        Args:
            blender_host: Blender socket server host
            blender_port: Blender socket server port
            api_key: Anthropic API key (optional, can use env var)
        """
        self.blender_host = blender_host
        self.blender_port = blender_port

        # Initialize Blender client
        self.blender = BlenderClient(blender_host, blender_port)

        # Initialize Anthropic client
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.anthropic = Anthropic(api_key=self.api_key)
        else:
            self.anthropic = None
            print("Warning: No Anthropic API key provided. Claude integration disabled.")

        self.conversation_history = []

    def connect_to_blender(self) -> bool:
        """
        Connect to Blender server.

        Returns:
            True if connected successfully
        """
        return self.blender.connect()

    def disconnect_from_blender(self) -> None:
        """Disconnect from Blender server."""
        self.blender.disconnect()

    async def process_prompt(self, prompt: str, model: str = "claude-3-7-sonnet-20250219") -> str:
        """
        Process user prompt with Claude and execute tools.

        Args:
            prompt: User prompt
            model: Claude model to use

        Returns:
            Response text
        """
        if not self.anthropic:
            return "Error: Anthropic API key not configured"

        if not self.blender.connected:
            return "Error: Not connected to Blender"

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })

        # System prompt
        system_prompt = """You are an AI assistant integrated with Blender 3D software.
You can control Blender through function calls to create, modify, and query 3D scenes.

Available operations:
- Create objects (cube, sphere, cylinder, plane)
- Move, rotate, scale objects
- Create and assign materials
- Execute Python code in Blender
- Query scene information

When the user asks you to do something in Blender, use the appropriate tools to accomplish it.
Be precise and provide clear feedback about what you did.
"""

        try:
            # Call Claude with tools
            response = self.anthropic.messages.create(
                model=model,
                max_tokens=4096,
                system=system_prompt,
                messages=self.conversation_history,
                tools=BLENDER_TOOLS,
            )

            # Process response
            result_text = ""
            tool_results = []

            for content_block in response.content:
                if content_block.type == "text":
                    result_text += content_block.text

                elif content_block.type == "tool_use":
                    # Execute tool
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_use_id = content_block.id

                    print(f"Executing tool: {tool_name}")
                    print(f"Input: {tool_input}")

                    # Execute tool on Blender
                    tool_result = execute_tool(self.blender, tool_name, tool_input)

                    print(f"Result: {tool_result}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps(tool_result)
                    })

            # If tools were used, get follow-up response
            if tool_results:
                # Add assistant's tool use to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Add tool results to history
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })

                # Get follow-up response
                follow_up = self.anthropic.messages.create(
                    model=model,
                    max_tokens=4096,
                    system=system_prompt,
                    messages=self.conversation_history,
                    tools=BLENDER_TOOLS,
                )

                # Extract text from follow-up
                for content_block in follow_up.content:
                    if content_block.type == "text":
                        result_text += "\n" + content_block.text

                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": follow_up.content
                })
            else:
                # No tools used, just add response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

            return result_text if result_text else "Done"

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return error_msg

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    async def run_interactive(self) -> None:
        """Run interactive prompt loop."""
        print("Blender MCP Server - Interactive Mode")
        print("=====================================")
        print()

        # Connect to Blender
        if not self.connect_to_blender():
            print("Failed to connect to Blender. Make sure:")
            print("1. Blender is running")
            print("2. LLM Prompting addon is enabled")
            print("3. Socket server is started")
            return

        print("Connected to Blender!")
        print()
        print("Type your prompts (or 'quit' to exit, 'clear' to clear history)")
        print()

        while True:
            try:
                # Get user input
                prompt = input("You: ").strip()

                if not prompt:
                    continue

                if prompt.lower() in ['quit', 'exit']:
                    break

                if prompt.lower() == 'clear':
                    self.clear_history()
                    print("Conversation history cleared.")
                    continue

                # Process prompt
                print("Assistant: ", end="", flush=True)
                response = await self.process_prompt(prompt)
                print(response)
                print()

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

        # Disconnect
        self.disconnect_from_blender()
        print("Disconnected from Blender.")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Blender MCP Server")
    parser.add_argument(
        "--host",
        default=os.getenv("BLENDER_HOST", "localhost"),
        help="Blender server host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("BLENDER_PORT", "9876")),
        help="Blender server port (default: 9876)"
    )
    parser.add_argument(
        "--model",
        default="claude-3-7-sonnet-20250219",
        help="Claude model to use"
    )

    args = parser.parse_args()

    # Create server
    server = BlenderMCPServer(
        blender_host=args.host,
        blender_port=args.port
    )

    # Run interactive mode
    asyncio.run(server.run_interactive())


if __name__ == "__main__":
    main()
