# Windows Local Setup Guide (stdio Mode)

This guide shows you how to run the DX Cluster MCP Server **locally on Windows 11** without Docker, using the **stdio transport** for direct integration with Claude Desktop.

## Overview

**stdio mode** runs the MCP server as a local process that communicates with Claude Desktop via standard input/output. This is perfect for:
- **Local development** on Windows without Docker
- **Quick testing** without setting up remote servers
- **Offline use** (server runs on your machine)
- **Simple setup** - no nginx, no API keys, no network configuration

```
┌──────────────────────┐
│  Claude Desktop      │
│    (Windows 11)      │
└──────────┬───────────┘
           │ stdio (stdin/stdout)
           │
┌──────────▼───────────┐
│  DX Cluster Server   │
│  (Python process)    │
└──────────┬───────────┘
           │ Telnet
           │
┌──────────▼───────────┐
│  DX Cluster          │
│  (e.g., NC7J)        │
└──────────────────────┘
```

## Prerequisites

- **Windows 11** (or Windows 10)
- **Python 3.11+** installed
- **Claude Desktop** installed
- **Git** (optional, for cloning the repository)
- **Valid Ham Radio Callsign**
- **Internet connection** to DX Cluster

## Step-by-Step Setup

### 1. Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Install Python 3.11 or newer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```cmd
   python --version
   ```
   Should show: `Python 3.11.x` or higher

### 2. Download the Server Code

**Option A: Using Git**
```cmd
git clone https://github.com/dgarcoe/dx_cluster_mcp.git
cd dx_cluster_mcp
```

**Option B: Download ZIP**
1. Download the repository as ZIP from GitHub
2. Extract to a folder (e.g., `C:\Users\YourName\dx_cluster_mcp`)
3. Open Command Prompt and navigate to the folder:
   ```cmd
   cd C:\Users\YourName\dx_cluster_mcp
   ```

### 3. Install Dependencies

```cmd
pip install -r requirements.txt
```

This installs:
- `fastmcp` - MCP server framework
- `telnetlib3` - Telnet client for DX Cluster
- `uvicorn` - ASGI server (not used in stdio mode, but required by fastmcp)
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

### 4. Configure Environment Variables

Create a `.env` file in the project directory:

```cmd
copy .env.example .env
notepad .env
```

Edit `.env` with your settings:

```env
# Your ham radio callsign (REQUIRED)
CALLSIGN=YOUR_CALLSIGN_HERE

# DX Cluster to connect to
DX_CLUSTER_HOST=dxc.nc7j.com
DX_CLUSTER_PORT=7373

# Transport type: stdio for local use
TRANSPORT=stdio

# API Key not needed for stdio mode
API_KEY=not-needed-for-stdio

# Server host/port not used in stdio mode
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

**Important**: Replace `YOUR_CALLSIGN_HERE` with your actual ham radio callsign!

### 5. Test the Server

Test that the server runs:

```cmd
python server.py --transport stdio
```

You should see:
```
Starting DX Cluster MCP Server
Transport: stdio
Cluster: dxc.nc7j.com:7373
Callsign: YOUR_CALLSIGN
Running in stdio mode for local Claude Desktop integration
API Key authentication: Disabled (stdio mode)
```

Press `Ctrl+C` to stop the test.

### 6. Configure Claude Desktop

1. **Locate the config file**:
   - Press `Win + R`
   - Type: `%APPDATA%\Claude`
   - Press Enter
   - Open or create `claude_desktop_config.json`

2. **Add the server configuration**:

```json
{
  "mcpServers": {
    "dx-cluster": {
      "command": "python",
      "args": [
        "C:\\Users\\YourName\\dx_cluster_mcp\\server.py",
        "--transport",
        "stdio"
      ],
      "env": {
        "CALLSIGN": "YOUR_CALLSIGN_HERE",
        "DX_CLUSTER_HOST": "dxc.nc7j.com",
        "DX_CLUSTER_PORT": "7373"
      }
    }
  }
}
```

**Important Notes:**
- Replace `C:\\Users\\YourName\\dx_cluster_mcp\\server.py` with the **full path** to your server.py file
- Use **double backslashes** (`\\`) in Windows paths
- Replace `YOUR_CALLSIGN_HERE` with your actual callsign

**Alternative**: If Python is in your PATH and you're in the right directory:

```json
{
  "mcpServers": {
    "dx-cluster": {
      "command": "python",
      "args": ["server.py", "--transport", "stdio"]
    }
  }
}
```

### 7. Restart Claude Desktop

1. **Completely close** Claude Desktop (check system tray)
2. **Start** Claude Desktop again
3. Wait for it to initialize (may take 10-30 seconds)

### 8. Test the Connection

In Claude Desktop, try these prompts:

```
Can you check the DX Cluster connection?
```

```
Show me the last 10 DX spots
```

```
What bands are most active right now?
```

**Expected Results:**
- ✅ Claude responds with DX Cluster information
- ✅ Can read spots from the cluster
- ✅ Can analyze band activity
- ✅ No connection errors

## Troubleshooting

### Issue: "Python is not recognized"

**Solution**: Python is not in your PATH.
```cmd
# Find Python installation
where python

# If not found, add Python to PATH:
# 1. Search for "Environment Variables" in Windows
# 2. Edit "Path" under System Variables
# 3. Add Python installation directory (e.g., C:\Python311)
# 4. Add Scripts directory (e.g., C:\Python311\Scripts)
# 5. Restart Command Prompt
```

### Issue: "No module named 'fastmcp'"

**Solution**: Dependencies not installed.
```cmd
pip install -r requirements.txt
```

### Issue: "Cannot connect to DX Cluster"

**Solution**: Check network and cluster availability.
```cmd
# Test telnet connection
telnet dxc.nc7j.com 7373

# If telnet doesn't work, try a different cluster:
# Edit .env and change:
DX_CLUSTER_HOST=hamqth.com
DX_CLUSTER_PORT=7300
```

### Issue: "MCP server not showing in Claude Desktop"

**Solutions**:
1. **Check config file syntax** (valid JSON):
   - No trailing commas
   - Proper quotes and brackets
   - Use [JSONLint](https://jsonlint.com/) to validate

2. **Check file paths**:
   - Use **absolute paths** (full path from C:\)
   - Use **double backslashes** (`\\`) in JSON

3. **Check logs** (if available):
   - Look for Claude Desktop log files
   - Check for error messages

4. **Restart completely**:
   - Close Claude Desktop
   - End any Python processes in Task Manager
   - Restart Claude Desktop

### Issue: "Permission denied" or "Access denied"

**Solution**: Run Command Prompt as Administrator:
1. Search for "Command Prompt"
2. Right-click → "Run as administrator"
3. Navigate to project directory
4. Install dependencies: `pip install -r requirements.txt`

### Issue: Server works but Claude can't connect

**Solutions**:
1. **Check environment variables in config**:
   ```json
   "env": {
     "CALLSIGN": "EA1RFI",  // Replace with your callsign
     "DX_CLUSTER_HOST": "dxc.nc7j.com",
     "DX_CLUSTER_PORT": "7373"
   }
   ```

2. **Test server manually**:
   ```cmd
   python server.py --transport stdio
   # Type: {"method": "tools/list"}
   # Should return list of available tools
   ```

3. **Check Python version**:
   ```cmd
   python --version
   # Must be 3.11 or higher
   ```

## Advanced Configuration

### Using a Different DX Cluster

Edit `.env` or Claude Desktop config:

**Popular DX Clusters:**
- **NC7J** (default): `dxc.nc7j.com:7373`
- **HamQTH**: `hamqth.com:7300`
- **W6CUA**: `w6cua.no-ip.org:7373`

Example in `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "dx-cluster": {
      "command": "python",
      "args": ["C:\\path\\to\\server.py", "--transport", "stdio"],
      "env": {
        "CALLSIGN": "EA1RFI",
        "DX_CLUSTER_HOST": "hamqth.com",
        "DX_CLUSTER_PORT": "7300"
      }
    }
  }
}
```

### Running Multiple Instances

You can connect to multiple DX Clusters by creating multiple server configurations:

```json
{
  "mcpServers": {
    "dx-cluster-nc7j": {
      "command": "python",
      "args": ["C:\\path\\to\\server.py", "--transport", "stdio"],
      "env": {
        "CALLSIGN": "EA1RFI",
        "DX_CLUSTER_HOST": "dxc.nc7j.com",
        "DX_CLUSTER_PORT": "7373"
      }
    },
    "dx-cluster-hamqth": {
      "command": "python",
      "args": ["C:\\path\\to\\server.py", "--transport", "stdio"],
      "env": {
        "CALLSIGN": "EA1RFI",
        "DX_CLUSTER_HOST": "hamqth.com",
        "DX_CLUSTER_PORT": "7300"
      }
    }
  }
}
```

### Using Virtual Environments (Recommended)

For better dependency management:

```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update Claude Desktop config to use venv Python:
# "command": "C:\\path\\to\\venv\\Scripts\\python.exe"
```

## Example Usage

Once configured, you can ask Claude:

**Basic Queries:**
- "Show me the last 20 DX spots"
- "Are there any stations on 20 meters?"
- "What's the band activity like?"

**Filtered Queries:**
- "Show me spots on 40 meters"
- "Find spots for EA1RFI"
- "Show me the last 50 spots on 15 meters"

**Analysis:**
- "What bands are most active right now?"
- "Which countries have been spotted in the last hour?"
- "What modes are being used?"
- "Analyze the propagation for the last 2 hours"

**Posting Spots:**
- "Post a spot for W1AW on 14.074 MHz, FT8 mode"
- "I heard EA1RFI on 7.074 MHz running FT8"

**Connection:**
- "Check if we're connected to the DX Cluster"
- "Show me the cluster information"

## Comparison: stdio vs SSE Mode

| Feature | stdio Mode (Local) | SSE Mode (Remote/Docker) |
|---------|-------------------|--------------------------|
| **Setup** | Simple (Python + config) | Complex (Docker + nginx) |
| **Network** | Not needed | Required |
| **API Key** | Not needed | Required |
| **Use Case** | Local development, personal use | Remote access, multi-user |
| **Platform** | Any OS with Python | Linux with Docker |
| **Security** | Local process only | Network authentication |
| **Performance** | Fast (local) | Network latency |

## Benefits of stdio Mode

✅ **Simple Setup** - No Docker, nginx, or network configuration
✅ **Fast** - No network latency, runs locally
✅ **Secure** - No exposed ports or API keys needed
✅ **Portable** - Works on any OS with Python
✅ **Easy Testing** - Great for development and debugging
✅ **Offline-Ready** - Only needs internet for DX Cluster connection

## When to Use Each Mode

**Use stdio mode when:**
- Running on Windows without Docker
- Personal local use
- Development and testing
- Single-user setup
- No need for remote access

**Use SSE mode when:**
- Deploying on a Linux server
- Need remote access from multiple machines
- Running in Docker/containers
- Multi-user environment
- Want centralized server

## Next Steps

After successful setup:

1. **Customize** your `.env` settings
2. **Explore** different DX Clusters
3. **Try** different analysis types
4. **Post spots** to the cluster
5. **Monitor** band activity for your favorite modes

## Getting Help

- **GitHub Issues**: [Report problems](https://github.com/dgarcoe/dx_cluster_mcp/issues)
- **Documentation**: See [README.md](README.md) for general info
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## References

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
- [DX Cluster Resources](https://www.dxcluster.info/)

73 and good DX!
