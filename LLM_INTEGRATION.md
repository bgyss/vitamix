# LLM Prompting Integration for Blender

This document describes the LLM (Large Language Model) integration added to Blender, enabling natural language control through AI assistants like Claude.

## Overview

The integration consists of two main components:

1. **Blender Addon** (`scripts/addons_core/llm_prompting/`) - Built into Blender
2. **MCP Server** (`blender_mcp_server/`) - External Python package

These components communicate via TCP sockets using a JSON-based protocol, following the Model Context Protocol (MCP) architecture.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
│  Claude Desktop / Claude CLI / Custom MCP Client                 │
└─────────────────────────────────────────────────────────────────┘
                              │ MCP Protocol
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Blender MCP Server (External)                 │
│  • Tool definitions for Blender operations                       │
│  • LLM provider integration (Claude, GPT, etc.)                  │
│  • Request/response handling                                     │
│  • Natural language processing                                   │
└─────────────────────────────────────────────────────────────────┘
                              │ JSON/TCP
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Blender Application                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         LLM Prompting Addon (Built-in)                    │  │
│  │  • Socket server (localhost:9876)                         │  │
│  │  • Command executor (safe Python execution)               │  │
│  │  • UI panels (3D View sidebar)                            │  │
│  │  • Scene context gathering                                │  │
│  │  • Conversation history tracking                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Blender Python API (bpy) → 3D Scene Manipulation                │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Approach

This integration follows **Approach A (MCP-Based)** from the research phase:

### Key Design Decisions

1. **Clean Separation**: Blender addon handles execution, MCP server handles AI
2. **Standards-Based**: Uses Model Context Protocol for LLM integration
3. **Socket Communication**: TCP with length-prefixed JSON messages
4. **Safe Execution**: Restricted Python environment with security checks
5. **Extensible**: Easy to add new operations and LLM providers

## Components

### 1. Blender Addon (`scripts/addons_core/llm_prompting/`)

**Purpose**: Provides the Blender-side infrastructure for LLM control.

**Key Files**:
- `__init__.py` - Addon registration and lifecycle
- `socket_server.py` - TCP server for MCP communication
- `command_executor.py` - Safe execution of operations and code
- `operators.py` - Blender operators for UI actions
- `panels.py` - UI panels in 3D View sidebar
- `properties.py` - Data structures for state management
- `utils.py` - Helper functions

**Features**:
- Socket server on localhost:9876
- 15+ built-in operations (create objects, materials, etc.)
- Safe Python code execution with restrictions
- Scene context awareness
- Conversation history
- Real-time status updates

### 2. MCP Server (`blender_mcp_server/`)

**Purpose**: External server that bridges LLMs and Blender.

**Key Files**:
- `server.py` - Main MCP server implementation
- `client.py` - Blender socket client
- `tools.py` - Tool definitions for Claude/GPT
- `pyproject.toml` - Package configuration

**Features**:
- Claude integration via Anthropic SDK
- 11+ tools for Blender operations
- Interactive prompt interface
- Tool use tracking and history
- Error handling and recovery

## Communication Protocol

### Message Format

**Request (MCP Server → Blender):**
```json
{
  "type": "execute_operation",
  "params": {
    "operation": "create_cube",
    "args": {"size": 2.0, "location": [0, 0, 0]}
  },
  "id": "msg_123"
}
```

**Response (Blender → MCP Server):**
```json
{
  "status": "success",
  "result": {
    "object_name": "Cube.001",
    "type": "MESH"
  },
  "id": "msg_123"
}
```

### Message Types

1. `execute_operation` - Execute structured operation
2. `execute_code` - Execute Python code
3. `get_context` - Get scene information
4. `ping` - Health check

## Installation & Setup

### 1. Enable Blender Addon

```
Blender → Edit → Preferences → Add-ons → Search "LLM Prompting" → Enable
```

### 2. Install MCP Server

```bash
cd blender_mcp_server
pip install -e .
export ANTHROPIC_API_KEY="your-key"
```

### 3. Start Components

**In Blender:**
- Open 3D View sidebar (N key)
- Go to LLM tab
- Click "Start Server"

**In Terminal:**
```bash
blender-mcp
```

### 4. Use It!

```
You: Create a red cube at position 2, 0, 0
Assistant: I've created a red cube at (2, 0, 0)...
```

## Available Operations

### Object Creation
- Create cube, sphere, cylinder, plane
- Configurable size, location, and segments

### Object Manipulation
- Move, scale, rotate objects
- Delete objects
- Select objects

### Materials
- Create materials with colors
- Assign materials to objects

### Scene Query
- Get scene information
- List objects and properties
- Query selection state

### Code Execution
- Execute arbitrary Python code (with restrictions)
- Validate code before running
- Access to bpy, math, mathutils

## Security Features

### Code Restrictions

Blocked operations:
- File system access (no `open`, `os`, `sys`)
- Process execution (no `subprocess`)
- Network access (no `socket`, `urllib`)
- Dynamic imports (no `__import__`)
- Code evaluation (no `eval`, `exec` in user code)

### Safe Environment

Allowed:
- `bpy` - Blender Python API
- `math`, `mathutils` - Math utilities
- Safe built-ins (range, len, etc.)
- Current context/scene data

### Network Security

- Socket server binds to localhost only
- No external network exposure by default
- Message size limits (10MB max)
- Connection timeout handling

## Usage Examples

### Natural Language Commands

```
"Create a scene with three cubes in a row"
"Make the first cube red, second blue, third green"
"Scale all cubes by 1.5"
"Move the camera to look at the cubes"
"Add a material to the active object"
```

### Python Code Generation

```
"Write code to create a spiral of 20 spheres"
"Generate a grid of cubes with random colors"
"Create an animation keyframe at frame 1"
```

### Scene Queries

```
"What objects are in my scene?"
"Show me the properties of the active object"
"List all materials"
```

## Integration with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "blender": {
      "command": "blender-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "your-key",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

## Development Workflow

### Testing the Addon

1. Enable addon in Blender
2. Start socket server
3. Use Python console to test:

```python
from llm_prompting.command_executor import get_executor
executor = get_executor()
result = executor.execute_operation("create_cube", {"size": 2.0}, bpy.context)
print(result)
```

### Testing the MCP Server

1. Start Blender with addon enabled
2. Run MCP server in debug mode:

```bash
python -m blender_mcp.server --host localhost --port 9876
```

3. Type prompts in terminal

### Adding New Operations

1. **Add executor method** in `command_executor.py`:
```python
def _op_my_operation(self, params, context):
    # Implementation
    return {"result": "data"}
```

2. **Add tool definition** in `tools.py`:
```python
{
    "name": "my_operation",
    "description": "Description",
    "input_schema": {...}
}
```

3. **Update documentation**

## Performance Considerations

- Socket communication is async, doesn't block UI
- Code execution happens in main thread (Blender requirement)
- Large operations may cause temporary UI freeze
- Consider batching multiple small operations

## Future Enhancements

### Planned Features

1. **Advanced Integrations**:
   - Poly Haven asset library
   - AI texture/material generation
   - 3D model generation (Hyper3D, Hunyuan3D)

2. **Multi-modal Support**:
   - Screenshot capture for vision models
   - Image-to-3D workflows
   - Video frame processing

3. **Enhanced Safety**:
   - Operation approval workflows
   - Undo/redo integration
   - Transaction rollback

4. **UI Improvements**:
   - In-viewport chat interface
   - Code editor with syntax highlighting
   - Visual operation preview

5. **Performance**:
   - Operation batching
   - Async execution where possible
   - Caching and optimization

## Related Research

This implementation was based on research of existing projects:

- **BlenderMCP** (ahujasid) - Socket-based MCP architecture
- **LLM-Blender-Agent** (saofund) - Multi-provider approach
- **BlenderLM** (victordibia) - Agent framework integration

See original research document in repository for full analysis.

## Troubleshooting

### Common Issues

**Server won't start:**
- Check if port 9876 is available
- Look for errors in Blender console
- Try different port in settings

**MCP server can't connect:**
- Verify Blender server is running
- Check host/port match
- Test with ping command

**Code execution fails:**
- Review code restrictions
- Check for blocked operations
- Look at error message details

### Debug Mode

Enable detailed logging:

```python
# In Blender Python console
from llm_prompting import utils
utils.log_debug("Debug message")
```

## Contributing

Contributions welcome! Areas for contribution:

1. New Blender operations
2. Additional LLM provider support
3. UI/UX improvements
4. Documentation and examples
5. Testing and bug fixes

Follow Blender's contribution guidelines and coding style.

## License

GPL-3.0-or-later (same as Blender)

This integration is part of Blender and follows the same licensing terms.

## Credits

**Developed by**: Blender Foundation
**Inspired by**: BlenderMCP, LLM-Blender-Agent, BlenderLM
**Architecture**: Model Context Protocol (MCP) by Anthropic

## Contact

- **Issues**: Blender issue tracker
- **Discussions**: devtalk.blender.org
- **Documentation**: developer.blender.org
