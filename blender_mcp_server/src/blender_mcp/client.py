# SPDX-FileCopyrightText: 2025 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Blender socket client for communication with Blender addon."""

import socket
import json
from typing import Dict, Any, Optional


class BlenderClient:
    """Client for communicating with Blender socket server."""

    def __init__(self, host: str = "localhost", port: int = 9876):
        """
        Initialize Blender client.

        Args:
            host: Blender server host
            port: Blender server port
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

    def connect(self, timeout: float = 5.0) -> bool:
        """
        Connect to Blender server.

        Args:
            timeout: Connection timeout in seconds

        Returns:
            True if connected successfully
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to Blender at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to Blender: {e}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from Blender server."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.connected = False

    def send_command(
        self,
        command_type: str,
        params: Dict[str, Any],
        message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send command to Blender.

        Args:
            command_type: Command type (e.g., 'execute_operation')
            params: Command parameters
            message_id: Optional message ID

        Returns:
            Response dictionary

        Raises:
            ConnectionError: If not connected to Blender
        """
        if not self.connected:
            raise ConnectionError("Not connected to Blender")

        # Construct message
        message = {
            "type": command_type,
            "params": params,
        }
        if message_id:
            message["id"] = message_id

        # Send message
        try:
            self._send_message(json.dumps(message))
            response_json = self._receive_message()
            return json.loads(response_json)
        except Exception as e:
            raise ConnectionError(f"Communication error: {e}")

    def execute_operation(self, operation: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a structured operation in Blender.

        Args:
            operation: Operation name (e.g., 'create_cube')
            args: Operation arguments

        Returns:
            Result dictionary
        """
        return self.send_command("execute_operation", {
            "operation": operation,
            "args": args
        })

    def execute_code(self, code: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute Python code in Blender.

        Args:
            code: Python code to execute
            dry_run: If True, validate without executing

        Returns:
            Result dictionary
        """
        return self.send_command("execute_code", {
            "code": code,
            "dry_run": dry_run
        })

    def get_context(self) -> Dict[str, Any]:
        """
        Get scene context from Blender.

        Returns:
            Scene context dictionary
        """
        return self.send_command("get_context", {})

    def ping(self) -> bool:
        """
        Ping Blender server.

        Returns:
            True if server responds
        """
        try:
            response = self.send_command("ping", {})
            return response.get("status") == "success"
        except:
            return False

    def _send_message(self, message: str) -> None:
        """Send message with length prefix."""
        message_bytes = message.encode('utf-8')
        length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
        self.socket.sendall(length_bytes + message_bytes)

    def _receive_message(self) -> str:
        """Receive message with length prefix."""
        # Read length prefix
        length_data = self._recv_exact(4)
        message_length = int.from_bytes(length_data, byteorder='big')

        # Read message
        message_data = self._recv_exact(message_length)
        return message_data.decode('utf-8')

    def _recv_exact(self, num_bytes: int) -> bytes:
        """Receive exactly num_bytes from socket."""
        data = b''
        while len(data) < num_bytes:
            chunk = self.socket.recv(num_bytes - len(data))
            if not chunk:
                raise ConnectionError("Connection closed")
            data += chunk
        return data

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
