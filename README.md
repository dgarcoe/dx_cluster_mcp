# DX Cluster MCP Server

A FastMCP-based Model Context Protocol (MCP) server for Ham Radio DX Cluster operations. This server enables Claude Desktop and other MCP clients to interact with DX Clusters for reading spots, posting spots, and analyzing propagation data.

## Features

- **Read DX Spots**: Retrieve recent DX spots with optional filtering by band or callsign
- **Post DX Spots**: Submit new DX spots to the cluster
- **Analyze Spots**: Perform statistical analysis on spots (band activity, country distribution, mode analysis)
- **Connection Management**: Check and manage DX Cluster connection status
- **SSE Transport**: Server-Sent Events transport for remote access
- **API Key Authentication**: Secure API key-based authentication
- **Docker Support**: Easy deployment with Docker and docker-compose

## Architecture

```
┌─────────────────────┐
│  Claude Desktop     │
│    (Windows)        │
└──────────┬──────────┘
           │ MCP Protocol (SSE + API Key)
           │
    ┌──────▼──────────┐
    │   MCP Proxy     │
    │   (Windows)     │
    └──────┬──────────┘
           │ HTTP/SSE
           │
    ┌──────▼──────────┐
    │  DX Cluster     │
    │  MCP Server     │
    │   (Docker)      │
    └──────┬──────────┘
           │ Telnet
           │
    ┌──────▼──────────┐
    │  DX Cluster     │
    │  (e.g. NC7J)    │
    └─────────────────┘
```

## Prerequisites

- Docker and Docker Compose
- Valid Ham Radio Callsign
- Network access to a DX Cluster (default: dxc.nc7j.com:7373)
- Claude Desktop (for Windows client)
- MCP Proxy (for remote connections)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd dx_cluster_mcp
```

### 2. Configure Environment

Copy the example environment file and edit it with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Your ham radio callsign (required)
CALLSIGN=EA1RFI

# DX Cluster connection (default is NC7J)
DX_CLUSTER_HOST=dxc.nc7j.com
DX_CLUSTER_PORT=7373

# API Key for authentication (generate a secure random string)
API_KEY=your-very-secure-random-api-key-here-change-me
```

**Important**: Change the `API_KEY` to a secure random string!

### 3. Create External Network

The server uses an external Docker network called `ea1rfi-network`. Create it before running docker-compose:

```bash
docker network create ea1rfi-network
```

### 4. Start the Server

```bash
docker-compose up -d
```

Check the logs:

```bash
docker-compose logs -f
```

The server will be available at `http://localhost:8000` (or your server's IP address).

## Configuration for Claude Desktop (Windows)

### Option 1: Using MCP Proxy (Recommended for Remote Access)

1. **Install MCP Proxy** on your Windows machine

2. **Configure MCP Proxy** to connect to your server:

Create or edit the MCP Proxy configuration file with the server URL and API key:

```json
{
  "dx-cluster": {
    "url": "http://your-server-ip:8000/sse",
    "headers": {
      "Authorization": "Bearer your-very-secure-random-api-key-here-change-me"
    }
  }
}
```

3. **Configure Claude Desktop** to use MCP Proxy

Edit Claude Desktop configuration file (typically at `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dx-cluster": {
      "command": "mcp-proxy",
      "args": ["dx-cluster"]
    }
  }
}
```

### Option 2: Direct SSE Connection (if supported)

If your MCP client supports direct SSE connections, configure it like this:

```json
{
  "mcpServers": {
    "dx-cluster": {
      "url": "http://your-server-ip:8000/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer your-very-secure-random-api-key-here-change-me"
      }
    }
  }
}
```

## Available Tools

### 1. `read_spots`

Read recent DX spots from the cluster.

**Parameters:**
- `count` (int, optional): Number of spots to retrieve (default: 10, max: 100)
- `band` (string, optional): Band filter (e.g., "20m", "40m", "15m")
- `callsign` (string, optional): Callsign filter to search for specific station

**Example:**
```json
{
  "count": 20,
  "band": "20m"
}
```

### 2. `post_spot`

Post a DX spot to the cluster.

**Parameters:**
- `frequency` (float): Frequency in MHz (e.g., 14.074 for 20m FT8)
- `dx_callsign` (string): Callsign of the station being spotted
- `comment` (string, optional): Comment about the spot (mode, signal report, etc.)

**Example:**
```json
{
  "frequency": 14.074,
  "dx_callsign": "EA1RFI",
  "comment": "FT8 +10dB"
}
```

### 3. `analyze_spots`

Analyze DX spots to provide insights and statistics.

**Parameters:**
- `hours` (int, optional): Number of hours to analyze (default: 1, max: 24)
- `analysis_type` (string): Type of analysis
  - `"summary"`: Overall statistics
  - `"bands"`: Spots per band distribution
  - `"countries"`: Spots per country prefix
  - `"modes"`: Spots per operating mode

**Example:**
```json
{
  "hours": 2,
  "analysis_type": "bands"
}
```

### 4. `check_connection`

Check the connection status to the DX Cluster.

**Parameters:** None

Returns connection status, cluster info, and configuration.

## Usage Examples

Once configured, you can interact with the DX Cluster through Claude Desktop:

**Example prompts:**

- "Show me the last 20 DX spots on 20 meters"
- "Post a spot for EA1RFI on 14.074 MHz with FT8"
- "Analyze the band activity for the last 3 hours"
- "What countries have been spotted in the last hour?"
- "Check if we're connected to the DX cluster"

## Troubleshooting

### Connection Issues

1. **Check server logs:**
   ```bash
   docker-compose logs -f
   ```

2. **Verify network connectivity:**
   ```bash
   docker exec dx-cluster-mcp-server ping dxc.nc7j.com
   ```

3. **Test telnet connection to cluster:**
   ```bash
   telnet dxc.nc7j.com 7373
   ```

### Authentication Errors

- Verify the API key matches between `.env` file and Claude Desktop configuration
- Check that the `Authorization` header is formatted correctly: `Bearer <your-api-key>`

### Docker Network Issues

- Ensure the external network exists:
  ```bash
  docker network ls | grep ea1rfi-network
  ```

- Recreate the network if needed:
  ```bash
  docker network rm ea1rfi-network
  docker network create ea1rfi-network
  ```

## Development

### Local Testing

For local development without Docker:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export CALLSIGN=N0CALL
   export DX_CLUSTER_HOST=dxc.nc7j.com
   export DX_CLUSTER_PORT=7373
   export API_KEY=test-key
   ```

3. Run the server:
   ```bash
   python server.py
   ```

### Testing Tools

You can test the MCP tools using the FastMCP CLI or MCP Inspector:

```bash
# Using FastMCP CLI
fastmcp dev server.py

# Or test with curl (SSE endpoint)
curl -H "Authorization: Bearer your-api-key" \
     http://localhost:8000/sse
```

## Security Considerations

- **API Key**: Always use a strong, randomly generated API key in production
- **Network Security**: Consider using HTTPS with a reverse proxy (nginx, traefik)
- **Firewall**: Restrict access to port 8000 to trusted IP addresses
- **Callsign**: Ensure you use your own licensed callsign
- **Cluster Rules**: Follow the rules and etiquette of the DX Cluster you're connecting to

## DX Cluster Resources

This server is compatible with standard DX Cluster software including:
- DXSpider
- AR-Cluster
- CC Cluster

Popular public DX Clusters:
- NC7J: dxc.nc7j.com:7373
- HamQTH: hamqth.com:7300
- W6CUA: w6cua.no-ip.org:7373

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## References

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [DX Cluster Resources](https://www.dxcluster.info/)
- [AR-Cluster User Manual](http://www.nc7j.com/arcluster/arusermanual-6/)

## Support

For issues and questions, please open an issue on GitHub.

73 de EA1RFI
