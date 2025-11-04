# SPDX-FileCopyrightText: 2025 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Socket server for MCP communication."""

import socket
import json
import threading
from queue import Queue, Empty
from typing import Dict, Any, Optional, Callable
from . import utils


class SocketServer:
    """TCP socket server for MCP communication."""

    def __init__(self, host: str = 'localhost', port: int = 9876):
        """
        Initialize socket server.

        Args:
            host: Server host address
            port: Server port
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.server_thread = None
        self.client_threads = []
        self.message_queue = Queue()
        self.command_handler = None

    def start(self) -> bool:
        """
        Start the socket server.

        Returns:
            True if started successfully
        """
        if self.running:
            utils.log_info("Server already running")
            return False

        try:
            # Create socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # Timeout for checking running flag

            self.running = True

            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()

            utils.log_info(f"Socket server started on {self.host}:{self.port}")
            return True

        except Exception as e:
            utils.log_error(f"Failed to start server: {utils.format_error_message(e)}")
            self.running = False
            if self.server_socket:
                self.server_socket.close()
            return False

    def stop(self) -> None:
        """Stop the socket server."""
        if not self.running:
            return

        utils.log_info("Stopping socket server...")
        self.running = False

        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        # Wait for server thread
        if self.server_thread:
            self.server_thread.join(timeout=2.0)

        # Clean up client threads
        for thread in self.client_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)

        self.client_threads.clear()
        utils.log_info("Socket server stopped")

    def set_command_handler(self, handler: Callable[[Dict], Dict]) -> None:
        """
        Set command handler function.

        Args:
            handler: Function that takes command dict and returns response dict
        """
        self.command_handler = handler

    def get_message(self, timeout: float = 0.01) -> Optional[Dict[str, Any]]:
        """
        Get next message from queue (non-blocking).

        Args:
            timeout: Timeout in seconds

        Returns:
            Message dictionary or None
        """
        try:
            return self.message_queue.get(timeout=timeout)
        except Empty:
            return None

    def _server_loop(self) -> None:
        """Main server loop (runs in thread)."""
        utils.log_debug("Server loop started")

        while self.running:
            try:
                # Accept connections (with timeout)
                client_socket, client_address = self.server_socket.accept()
                utils.log_info(f"Client connected: {client_address}")

                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
                self.client_threads.append(client_thread)

            except socket.timeout:
                # Normal timeout, continue loop
                continue
            except Exception as e:
                if self.running:  # Only log if we're supposed to be running
                    utils.log_error(f"Server loop error: {utils.format_error_message(e)}")
                break

        utils.log_debug("Server loop ended")

    def _handle_client(self, client_socket: socket.socket, client_address: tuple) -> None:
        """
        Handle client connection.

        Args:
            client_socket: Client socket
            client_address: Client address tuple
        """
        try:
            client_socket.settimeout(30.0)  # 30 second timeout for client operations

            while self.running:
                # Receive data
                data = self._receive_message(client_socket)
                if not data:
                    break

                utils.log_debug(f"Received: {data[:100]}...")

                # Parse JSON
                try:
                    message = json.loads(data)
                except json.JSONDecodeError as e:
                    utils.log_error(f"Invalid JSON: {e}")
                    response = {
                        "status": "error",
                        "message": "Invalid JSON"
                    }
                    self._send_message(client_socket, json.dumps(response))
                    continue

                # Process message
                response = self._process_message(message)

                # Send response
                response_json = json.dumps(response)
                self._send_message(client_socket, response_json)

        except Exception as e:
            utils.log_error(f"Client handler error: {utils.format_error_message(e)}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            utils.log_info(f"Client disconnected: {client_address}")

    def _receive_message(self, client_socket: socket.socket) -> Optional[str]:
        """
        Receive message from client.

        Messages are length-prefixed: 4 bytes (big-endian int) + message data

        Args:
            client_socket: Client socket

        Returns:
            Message string or None
        """
        try:
            # Read length prefix (4 bytes)
            length_data = self._recv_exact(client_socket, 4)
            if not length_data:
                return None

            message_length = int.from_bytes(length_data, byteorder='big')

            # Sanity check
            if message_length > 10 * 1024 * 1024:  # 10 MB limit
                utils.log_error(f"Message too large: {message_length} bytes")
                return None

            # Read message data
            message_data = self._recv_exact(client_socket, message_length)
            if not message_data:
                return None

            return message_data.decode('utf-8')

        except Exception as e:
            utils.log_error(f"Receive error: {utils.format_error_message(e)}")
            return None

    def _send_message(self, client_socket: socket.socket, message: str) -> bool:
        """
        Send message to client.

        Args:
            client_socket: Client socket
            message: Message string

        Returns:
            True if sent successfully
        """
        try:
            message_bytes = message.encode('utf-8')
            length_bytes = len(message_bytes).to_bytes(4, byteorder='big')

            # Send length prefix + message
            client_socket.sendall(length_bytes + message_bytes)
            return True

        except Exception as e:
            utils.log_error(f"Send error: {utils.format_error_message(e)}")
            return False

    def _recv_exact(self, client_socket: socket.socket, num_bytes: int) -> Optional[bytes]:
        """
        Receive exactly num_bytes from socket.

        Args:
            client_socket: Client socket
            num_bytes: Number of bytes to receive

        Returns:
            Bytes or None
        """
        data = b''
        while len(data) < num_bytes:
            chunk = client_socket.recv(num_bytes - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def _process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message.

        Args:
            message: Message dictionary

        Returns:
            Response dictionary
        """
        # Add to queue for processing by Blender
        self.message_queue.put(message)

        # If command handler is set, call it directly
        if self.command_handler:
            try:
                response = self.command_handler(message)
                return response
            except Exception as e:
                utils.log_error(f"Command handler error: {utils.format_error_message(e)}")
                return {
                    "status": "error",
                    "message": utils.format_error_message(e),
                    "id": message.get('id')
                }

        # Default response (queued for processing)
        return {
            "status": "queued",
            "message": "Command queued for processing",
            "id": message.get('id')
        }

    def is_running(self) -> bool:
        """Check if server is running."""
        return self.running


# Global server instance
_server = None


def get_server() -> SocketServer:
    """Get global socket server instance."""
    global _server
    if _server is None:
        _server = SocketServer()
    return _server
