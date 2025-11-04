# Blender MCP Server

Model Context Protocol (MCP) server for Blender integration. Enables natural language control of Blender through AI assistants like Claude.

## Overview

This MCP server acts as a bridge between Large Language Models (LLMs) and Blender, allowing you to:

- Create and modify 3D objects using natural language
- Control scene composition through AI prompts
- Execute Python code in Blender safely
- Query scene information and context

## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Claude AI /   │  MCP    │  Blender MCP    │  TCP    │  Blender Addon  │
│   Other LLM     │ ◄─────► │     Server      │ ◄─────► │  Socket Server  │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Blender 4.4+ with LLM Prompting addon enabled
- Anthropic API key (for Claude integration)

### Install from source

```bash
cd blender_mcp_server
pip install -e .
```

### Install dependencies only

```bash
pip install anthropic mcp
```

## Configuration

### Environment Variables

```bash
# Anthropic API key (required for Claude)
export ANTHROPIC_API_KEY="your-api-key-here"

# Blender server settings (optional)
export BLENDER_HOST="localhost"
export BLENDER_PORT="9876"
```

## Usage

### 1. Start Blender and Enable Addon

1. Open Blender
2. Go to Edit → Preferences → Add-ons
3. Search for "LLM Prompting"
4. Enable the addon
5. Go to 3D View → Sidebar (N key) → LLM tab
6. Click "Start Server"

### 2. Run MCP Server

#### Interactive Mode

```bash
blender-mcp
```

This starts an interactive prompt where you can type natural language commands:

```
You: Create a red cube at position 2, 0, 0
Assistant: I've created a red cube at position (2, 0, 0)...

You: Add a blue sphere next to it
Assistant: I've added a blue sphere at position (4, 0, 0)...
```

#### Custom Configuration

```bash
blender-mcp --host localhost --port 9876 --model claude-3-7-sonnet-20250219
```

### 3. Use with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "blender": {
      "command": "blender-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

## Available Tools

The MCP server provides the following tools to Claude:

### Object Creation
- `create_cube` - Create a cube with size and location
- `create_sphere` - Create a sphere with radius and location
- `create_cylinder` - Create a cylinder with radius and height

### Object Manipulation
- `move_object` - Move object to new location
- `scale_object` - Scale object uniformly or non-uniformly
- `rotate_object` - Rotate object in radians
- `delete_object` - Delete object from scene

### Materials
- `create_material` - Create material with color
- `assign_material` - Assign material to object

### Scene Query
- `get_scene_info` - Get current scene information

### Code Execution
- `execute_python` - Execute Python code in Blender (use with caution)

## Example Prompts

Here are some example prompts you can use:

```
"Create a simple scene with a cube, sphere, and cylinder"

"Make the cube red and move it to position 2, 0, 0"

"Create a grid of 5x5 spheres spaced 2 units apart"

"Rotate the active object 45 degrees around the Z axis"

"Show me what objects are currently in the scene"

"Write Python code to create a spiral of cubes"
```

## Development

### Project Structure

```
blender_mcp_server/
├── src/
│   └── blender_mcp/
│       ├── __init__.py       # Package init
│       ├── server.py          # Main MCP server
│       ├── client.py          # Blender socket client
│       └── tools.py           # Tool definitions
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

### Running Tests

```bash
pytest
```

### Code Style

```bash
# Format code
black src/

# Lint code
ruff check src/
```

## Troubleshooting

### "Failed to connect to Blender"

1. Make sure Blender is running
2. Check that LLM Prompting addon is enabled
3. Verify socket server is started (in LLM panel)
4. Check host/port settings match

### "Error: Anthropic API key not configured"

Set the `ANTHROPIC_API_KEY` environment variable:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Connection timeout

Increase the connection timeout or check firewall settings:

```python
# In client.py
client.connect(timeout=10.0)  # Increase timeout
```

## Security Considerations

- The server executes code in Blender - only use with trusted prompts
- Code execution has restrictions but is not fully sandboxed
- Socket server is localhost-only by default
- Consider using authentication tokens in production

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

GPL-3.0-or-later

See Blender's license at: https://www.blender.org/about/license/

## Related Projects

- [BlenderMCP](https://github.com/ahujasid/blender-mcp) - Original inspiration
- [LLM-Blender-Agent](https://github.com/saofund/LLM-Blender-Agent) - Multi-provider approach
- [BlenderLM](https://github.com/victordibia/blenderlm) - Agent framework integration

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review Blender's developer documentation
