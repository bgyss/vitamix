# LLM Prompting Addon for Blender

Natural language control of Blender through Large Language Model integration via Model Context Protocol (MCP).

## Features

- **Socket Server**: TCP server for MCP communication
- **Safe Code Execution**: Restricted Python execution environment
- **Natural Language Prompts**: Control Blender through AI assistants
- **Scene Context Awareness**: Auto-include scene information in prompts
- **Conversation History**: Track interactions and responses
- **Multiple LLM Support**: Works with Claude, GPT, and local models

## Installation

### From Blender (Built-in)

This addon is included in Blender 4.4+ as a core addon:

1. Open Blender
2. Go to Edit → Preferences → Add-ons
3. Search for "LLM Prompting"
4. Enable the checkbox

### Manual Installation (Development)

1. Copy `llm_prompting` folder to Blender's addons directory:
   - **Linux**: `~/.config/blender/4.4/scripts/addons/`
   - **macOS**: `~/Library/Application Support/Blender/4.4/scripts/addons/`
   - **Windows**: `%APPDATA%\Blender Foundation\Blender\4.4\scripts\addons\`

2. Restart Blender or reload scripts (F3 → Reload Scripts)
3. Enable in Preferences → Add-ons

## Quick Start

### 1. Enable and Start Server

1. Open Blender
2. Press `N` in 3D View to open sidebar
3. Click on "LLM" tab
4. Click "Start Server" button

The socket server is now listening on `localhost:9876` (default).

### 2. Run External MCP Server

In a terminal:

```bash
cd blender_mcp_server
pip install -e .
export ANTHROPIC_API_KEY="your-key"
blender-mcp
```

### 3. Send Prompts

Type natural language commands in the MCP server terminal:

```
You: Create a red cube
You: Add a blue sphere next to it
You: Make the cube twice as large
```

## User Interface

### Main Panel (View3D → Sidebar → LLM)

- **Status**: Shows server status and current state
- **Server Controls**: Start/stop socket server
- **Server Settings**: Configure host and port

### Prompt Panel

- **Prompt Input**: Enter natural language prompts
- **Send Button**: Execute prompt
- **Add Context**: Add current scene context to prompt
- **Include Scene Context**: Auto-include context in prompts

### Conversation Panel

- **Message History**: View recent conversation messages
- **Last Response**: Display last LLM response
- **Clear Button**: Clear conversation history
- **Copy Response**: Copy response to clipboard

### Code Preview Panel

- **Generated Code**: View LLM-generated Python code
- **Execute Button**: Run the generated code
- **Auto Execute**: Automatically execute without preview

### Settings Panel

- **Provider**: Select LLM provider (Claude, OpenAI, Local)
- **Model Name**: Specify model identifier
- **Temperature**: Control response randomness
- **Max Tokens**: Set response length limit
- **Security Options**: Code restrictions and confirmations

## Configuration

### Addon Preferences

Access via Edit → Preferences → Add-ons → LLM Prompting

- **Auto-start Server**: Start server when Blender launches
- **API Keys**: Configure Claude/OpenAI API keys (optional)
- **Local Endpoint**: URL for local models (e.g., Ollama)

### Server Settings

In the LLM panel:

- **Host**: Server host address (default: localhost)
- **Port**: Server port (default: 9876)

## Available Operations

The addon supports these operations via socket commands:

### Object Creation
```json
{"type": "execute_operation", "params": {"operation": "create_cube", "args": {"size": 2.0, "location": [0, 0, 0]}}}
```

### Object Manipulation
```json
{"type": "execute_operation", "params": {"operation": "move_object", "args": {"name": "Cube", "location": [2, 0, 0]}}}
```

### Code Execution
```json
{"type": "execute_code", "params": {"code": "import bpy\nbpy.ops.mesh.primitive_cube_add()", "dry_run": false}}
```

### Scene Query
```json
{"type": "get_context", "params": {}}
```

## Socket Protocol

Messages are length-prefixed JSON over TCP:

1. **Length Prefix**: 4 bytes (big-endian integer)
2. **Message Data**: UTF-8 encoded JSON

### Message Format

**Request:**
```json
{
  "type": "execute_operation",
  "params": {
    "operation": "create_cube",
    "args": {"size": 2.0}
  },
  "id": "msg_123"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {"object_name": "Cube.001"},
  "id": "msg_123"
}
```

## Security

### Code Restrictions

When enabled, the following are blocked:

- File system access (`open`, `os`, `sys`)
- Process execution (`subprocess`)
- Dynamic imports (`__import__`, `importlib`)
- Code evaluation (`eval`, `exec`, `compile`)

### Safe Execution

Code runs in restricted environment with only:

- `bpy` (Blender Python API)
- `math`, `mathutils` modules
- Safe built-in functions
- Current context/scene data

### Best Practices

1. Keep "Require Confirmation" enabled
2. Review generated code before execution
3. Use "Code Restrictions" for untrusted sources
4. Run server on localhost only
5. Don't expose server to public networks

## Troubleshooting

### Server Won't Start

- Check if port 9876 is already in use
- Try a different port in settings
- Check Blender console for error messages

### No Response from MCP

- Verify server is running (check status)
- Ensure MCP server is connected
- Check connection with "Test Connection" button

### Code Execution Fails

- Check code restrictions settings
- Review generated code for issues
- Look for error messages in conversation
- Check Blender system console (Window → Toggle System Console)

### Permission Errors

- Ensure Blender has network permissions
- Check firewall settings
- Verify localhost is accessible

## Development

### Project Structure

```
llm_prompting/
├── __init__.py           # Main addon file, registration
├── properties.py         # Property definitions
├── operators.py          # Blender operators
├── panels.py            # UI panels
├── socket_server.py     # TCP socket server
├── command_executor.py  # Safe code execution
├── utils.py             # Helper functions
└── README.md            # This file
```

### Adding New Operations

1. Add operation handler to `command_executor.py`:

```python
def _op_my_operation(self, params: Dict, context: bpy.types.Context):
    # Implementation
    return {"result": "data"}
```

2. Add tool definition to MCP server's `tools.py`

3. Update documentation

### Testing

Test addon in Blender:

```python
import bpy

# Enable addon
bpy.ops.preferences.addon_enable(module="llm_prompting")

# Start server
bpy.ops.llm.toggle_server()

# Test command
from llm_prompting.command_executor import get_executor
executor = get_executor()
result = executor.execute_operation("create_cube", {"size": 2.0}, bpy.context)
print(result)
```

## API Reference

### Properties (scene.llm_prompting)

- `prompt_input` (str): Current prompt text
- `last_response` (str): Last LLM response
- `conversation` (collection): Message history
- `server_enabled` (bool): Server running state
- `server_host` (str): Server host
- `server_port` (int): Server port
- `model_provider` (enum): LLM provider
- `preview_code` (str): Generated code preview

### Operators

- `llm.toggle_server`: Start/stop socket server
- `llm.execute_prompt`: Send prompt to conversation
- `llm.execute_code_preview`: Execute previewed code
- `llm.clear_conversation`: Clear history
- `llm.test_connection`: Test server status
- `llm.add_context_to_prompt`: Add scene context

## Examples

### Create Objects

```python
# Via prompt (in MCP terminal)
"Create a cube at position 2, 0, 0"
"Add a blue sphere next to the cube"
```

### Execute Python

```python
# Via MCP
"Run this code: for i in range(5): bpy.ops.mesh.primitive_cube_add(location=(i*2, 0, 0))"
```

### Query Scene

```python
# Via prompt
"What objects are in my scene?"
"Show me the location of the active object"
```

## Contributing

Contributions welcome! Please:

1. Follow Blender's code style (see `.clang-format`)
2. Add docstrings to functions
3. Include type hints
4. Test with multiple Blender versions
5. Update documentation

## License

GPL-3.0-or-later

Part of Blender, licensed under GNU GPL v3.

## Credits

Inspired by:
- BlenderMCP by Siddharth Ahuja
- LLM-Blender-Agent by saofund
- BlenderLM by Victor Dibia

## Support

- **Documentation**: See Blender developer docs
- **Issues**: Report on Blender tracker
- **Community**: devtalk.blender.org
