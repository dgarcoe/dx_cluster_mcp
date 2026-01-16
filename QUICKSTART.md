# Quick Start Guide

Get your DX Cluster MCP Server running in 5 minutes!

## Server Setup (Linux/Docker)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit with your callsign and API key
nano .env
# Set CALLSIGN=YOUR_CALLSIGN
# Set API_KEY=generate-secure-random-key

# 3. Create network
docker network create ea1rfi-network

# 4. Start server
docker-compose up -d --build

# 5. Check logs
docker-compose logs -f
```

**Server will be available at**: `http://localhost:8000`

## Windows Client Setup (Claude Desktop)

1. **Open Config File**: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add Configuration**:
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
        "MCP_AUTH_HEADER": "Authorization: Bearer YOUR-API-KEY"
      }
    }
  }
}
```

3. **Replace**:
   - `YOUR-SERVER-IP` → Your server's IP address
   - `YOUR-API-KEY` → API key from server's .env file

4. **Restart Claude Desktop**

## Test Connection

In Claude Desktop, ask:

```
Can you check the DX Cluster connection?
```

or

```
Show me the last 10 DX spots
```

## Common Commands

| What you want | Ask Claude |
|--------------|------------|
| See recent spots | "Show me the last 20 DX spots" |
| Filter by band | "Show me spots on 20 meters" |
| Post a spot | "Post a spot for EA1RFI on 14.074 MHz, FT8" |
| Band activity | "What bands are most active?" |
| Country stats | "Which countries have been spotted?" |
| Mode analysis | "What modes are being used?" |

## Troubleshooting

**Can't connect?**
```bash
# Check server status
docker-compose ps
docker-compose logs -f

# Test from browser
http://YOUR-SERVER-IP:8000/
```

**Authentication failed?**
- Check API key matches in both `.env` and `claude_desktop_config.json`
- Format: `Authorization: Bearer YOUR-KEY` (with space after Bearer)

**Server not starting?**
```bash
# Check network exists
docker network ls | grep ea1rfi-network

# Create if missing
docker network create ea1rfi-network

# Restart
docker-compose restart
```

## Need More Help?

- **Full Windows Setup**: See [SETUP_WINDOWS.md](SETUP_WINDOWS.md)
- **Complete Documentation**: See [README.md](README.md)
- **DX Cluster Info**: https://www.dxcluster.info/

## Security Note

⚠️ **Always use a strong, random API key in production!**

Generate one with:
```bash
openssl rand -hex 32
```

## Popular DX Clusters

Default: `dxc.nc7j.com:7373`

Others:
- `hamqth.com:7300`
- `w6cua.no-ip.org:7373`
- `dxc.wa9pie.net:8000`

Change in `.env`:
```env
DX_CLUSTER_HOST=hamqth.com
DX_CLUSTER_PORT=7300
```

73!
