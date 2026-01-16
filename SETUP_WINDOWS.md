# Windows Setup Guide for DX Cluster MCP Server

This guide walks you through setting up the DX Cluster MCP Server and connecting it to Claude Desktop on Windows using MCP Proxy.

## Overview

```
┌──────────────────────┐
│  Claude Desktop      │  (Windows)
│  %APPDATA%\Claude    │
└──────────┬───────────┘
           │ Uses MCP Proxy
           ▼
┌──────────────────────┐
│  MCP Proxy           │  (Windows - npx)
│  @modelcontextprotocol/
│  server-proxy        │
└──────────┬───────────┘
           │ HTTP/SSE + API Key
           ▼
┌──────────────────────┐
│  DX Cluster Server   │  (Docker/Remote Server)
│  Port 8000           │
└──────────┬───────────┘
           │ Telnet
           ▼
┌──────────────────────┐
│  DX Cluster          │  (Internet)
│  (e.g., NC7J)        │
└──────────────────────┘
```

## Prerequisites

### On the Server (Linux/Docker):
- Docker and Docker Compose installed
- Open port 8000 (or your chosen port)
- Network access to a DX Cluster

### On Windows (Client):
- Claude Desktop installed
- Node.js and npm installed (for MCP Proxy)
- Network access to the server

## Part 1: Server Setup

### Step 1: Prepare the Server

1. **Clone or copy the project files** to your Docker host:
   ```bash
   git clone <repository-url>
   cd dx_cluster_mcp
   ```

2. **Create the environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env`** with your settings:
   ```bash
   nano .env
   ```

   ```env
   # Your ham radio callsign (REQUIRED)
   CALLSIGN=EA1RFI

   # DX Cluster to connect to
   DX_CLUSTER_HOST=dxc.nc7j.com
   DX_CLUSTER_PORT=7373

   # IMPORTANT: Generate a secure random API key!
   # Use a password generator or run: openssl rand -hex 32
   API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
   ```

4. **Save and exit** (Ctrl+X, then Y, then Enter in nano)

### Step 2: Create the Docker Network

```bash
docker network create ea1rfi-network
```

### Step 3: Start the Server

```bash
docker-compose up -d --build
```

### Step 4: Verify the Server is Running

```bash
# Check logs
docker-compose logs -f

# You should see something like:
# Starting DX Cluster MCP Server
# Cluster: dxc.nc7j.com:7373
# Callsign: EA1RFI
# API Key authentication: Enabled
```

### Step 5: Test the Server

```bash
# From another terminal or machine:
curl http://YOUR-SERVER-IP:8000/
```

You should get a response indicating the server is running.

### Step 6: Note Your Connection Details

Write down:
- **Server IP/Hostname**: `_________________`
- **Port**: `8000` (or your custom port)
- **API Key**: `_________________` (from your .env file)

## Part 2: Windows Client Setup

### Step 1: Install Node.js (if not already installed)

1. Download from: https://nodejs.org/
2. Install the LTS version
3. Verify installation:
   ```cmd
   node --version
   npm --version
   ```

### Step 2: Locate Claude Desktop Config File

The configuration file is located at:
```
%APPDATA%\Claude\claude_desktop_config.json
```

To open the folder:
1. Press `Win + R`
2. Type: `%APPDATA%\Claude`
3. Press Enter

### Step 3: Edit Claude Desktop Configuration

Open `claude_desktop_config.json` in a text editor (Notepad++ recommended).

If the file doesn't exist, create it.

Add or modify the configuration:

```json
{
  "mcpServers": {
    "dx-cluster": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-proxy",
        "http://YOUR-SERVER-IP:8000/sse"
      ],
      "env": {
        "MCP_AUTH_HEADER": "Authorization: Bearer YOUR-API-KEY-HERE"
      }
    }
  }
}
```

**Replace:**
- `YOUR-SERVER-IP` with your server's IP address or hostname
- `YOUR-API-KEY-HERE` with the API key from your server's .env file

**Example:**
```json
{
  "mcpServers": {
    "dx-cluster": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-proxy",
        "http://192.168.1.100:8000/sse"
      ],
      "env": {
        "MCP_AUTH_HEADER": "Authorization: Bearer abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

1. Completely close Claude Desktop (check system tray)
2. Start Claude Desktop again
3. Wait for it to connect to the MCP server

### Step 5: Verify Connection

In Claude Desktop, try these prompts:

1. **Check connection:**
   ```
   Can you check if you're connected to the DX Cluster?
   ```

2. **Read spots:**
   ```
   Show me the last 10 DX spots
   ```

3. **Analyze activity:**
   ```
   What bands are most active right now?
   ```

## Troubleshooting

### Issue: "Cannot connect to server"

**Solutions:**
1. Verify server is running:
   ```bash
   docker-compose ps
   ```

2. Check server logs:
   ```bash
   docker-compose logs -f
   ```

3. Test connection from Windows:
   ```cmd
   curl http://YOUR-SERVER-IP:8000/
   ```
   Or open in browser: `http://YOUR-SERVER-IP:8000/`

4. Check firewall on server (allow port 8000)

5. Check Windows firewall

### Issue: "Authentication failed" or 401 errors

**Solutions:**
1. Verify API key matches between:
   - Server: `.env` file
   - Client: `claude_desktop_config.json`

2. Ensure API key format is correct:
   ```json
   "MCP_AUTH_HEADER": "Authorization: Bearer YOUR-KEY"
   ```
   (Note: "Bearer" with capital B, followed by a space)

3. Restart server after changing API key:
   ```bash
   docker-compose restart
   ```

### Issue: "MCP server not showing up in Claude"

**Solutions:**
1. Check `claude_desktop_config.json` syntax (valid JSON)
2. Verify file location: `%APPDATA%\Claude\claude_desktop_config.json`
3. Restart Claude Desktop completely
4. Check Claude Desktop logs (if available)

### Issue: "npx command not found"

**Solutions:**
1. Install Node.js from https://nodejs.org/
2. Restart Command Prompt/PowerShell
3. Verify: `npx --version`

### Issue: Connection to DX Cluster fails

**Solutions:**
1. Check server logs:
   ```bash
   docker-compose logs -f
   ```

2. Test telnet from server:
   ```bash
   docker exec -it dx-cluster-mcp-server bash
   telnet dxc.nc7j.com 7373
   ```

3. Try a different DX Cluster:
   Edit `.env` and change:
   ```env
   DX_CLUSTER_HOST=hamqth.com
   DX_CLUSTER_PORT=7300
   ```

4. Restart server:
   ```bash
   docker-compose restart
   ```

## Advanced Configuration

### Using HTTPS

For production use, consider using HTTPS with a reverse proxy:

1. **Install nginx or Caddy** on your server
2. **Configure reverse proxy** to forward to localhost:8000
3. **Get SSL certificate** (Let's Encrypt)
4. **Update Claude config** to use https://

Example Caddy configuration:
```
dxcluster.yourdomain.com {
    reverse_proxy localhost:8000
}
```

### Firewall Configuration

If using `ufw` on Ubuntu:
```bash
sudo ufw allow 8000/tcp
sudo ufw reload
```

If using `firewalld` on CentOS/RHEL:
```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### Custom Port

To use a different port:

1. Edit `docker-compose.yml`:
   ```yaml
   ports:
     - "9000:8000"  # External:Internal
   ```

2. Restart:
   ```bash
   docker-compose up -d
   ```

3. Update Claude config with new port

## Security Best Practices

1. **Strong API Key**: Use a long, random API key (32+ characters)
   ```bash
   # Generate on Linux:
   openssl rand -hex 32

   # Or on Windows with PowerShell:
   -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | % {[char]$_})
   ```

2. **Firewall**: Restrict port 8000 to known IP addresses only

3. **HTTPS**: Use HTTPS in production with valid certificates

4. **Regular Updates**: Keep Docker images and dependencies updated

5. **Monitoring**: Monitor server logs for suspicious activity

## Testing the Connection

### Test 1: Basic Connectivity
```cmd
curl http://YOUR-SERVER-IP:8000/
```

### Test 2: SSE Endpoint with Authentication
```cmd
curl -H "Authorization: Bearer YOUR-API-KEY" http://YOUR-SERVER-IP:8000/sse
```

### Test 3: Direct MCP Proxy Test
```cmd
npx @modelcontextprotocol/server-proxy http://YOUR-SERVER-IP:8000/sse
```

## Example Usage in Claude Desktop

Once connected, you can ask Claude:

- "Show me the last 20 spots on 20 meters"
- "What's the band activity like right now?"
- "Post a spot for EA1RFI on 14.074 MHz, FT8 mode"
- "Which countries have been active in the last 2 hours?"
- "Analyze the propagation on 15 meters"
- "Is there any 6 meter activity?"
- "What modes are most popular right now?"

## Getting Help

If you encounter issues:

1. Check server logs: `docker-compose logs -f`
2. Review this troubleshooting guide
3. Check GitHub issues
4. Post a new issue with:
   - Server logs
   - Claude Desktop logs (if available)
   - Your configuration (redact API key!)

## Uninstalling

To remove the server:

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi dx_cluster_mcp_dx-cluster-mcp

# Remove network
docker network rm ea1rfi-network

# Remove files
cd ..
rm -rf dx_cluster_mcp
```

On Windows, remove the `dx-cluster` section from `claude_desktop_config.json`.

## Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop Documentation](https://claude.ai/desktop)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [DX Cluster Resources](https://www.dxcluster.info/)

73 and good DX!
