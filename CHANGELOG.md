# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-19

### Added
- **stdio Transport Mode**: Server now supports running locally without Docker
  - New `--transport` command-line argument to choose between stdio and SSE modes
  - Perfect for Windows 11/10 users who want to run locally
  - No API key required in stdio mode (local process only)
  - No network configuration needed (direct stdin/stdout communication)
- **SETUP_WINDOWS_LOCAL.md**: Comprehensive guide for local Windows setup
  - Step-by-step installation instructions
  - Python environment setup
  - Claude Desktop configuration for stdio mode
  - Troubleshooting section for common Windows issues
  - Virtual environment setup instructions
- **Dual Configuration Example**: Updated `claude_desktop_config.json` with both stdio and SSE examples
- **Enhanced Documentation**:
  - Updated README.md with deployment options comparison
  - Updated QUICKSTART.md with local setup section
  - Architecture diagrams for both transport modes
  - Prerequisites split by deployment mode

### Changed
- Server startup now uses argparse for command-line options
- Print statements now use stderr to avoid interfering with stdio transport
- Environment variables can be used to set default transport, host, and port
- `.env.example` updated with TRANSPORT variable

### Fixed
- Proper error handling for both transport modes
- Correct output redirection for stdio mode

### Benefits of stdio Mode
- ✅ Simple setup - No Docker, nginx, or network configuration required
- ✅ Fast - No network latency, runs locally
- ✅ Secure - No exposed ports or API keys needed
- ✅ Portable - Works on Windows, Mac, and Linux with just Python
- ✅ Easy testing - Great for development and debugging

## [1.0.0] - 2026-01-16

### Added
- Initial release of DX Cluster MCP Server
- FastMCP-based server implementation with SSE transport
- API Key authentication middleware
- Four main tools:
  - `read_spots`: Read recent DX spots with filtering options
  - `post_spot`: Post new DX spots to the cluster
  - `analyze_spots`: Analyze spots with statistics (summary, bands, countries, modes)
  - `check_connection`: Verify cluster connection status
- Telnet connection to DX Cluster with automatic reconnection
- Spot parsing and data extraction
- Band identification from frequency
- Country prefix extraction from callsign
- Mode detection from comments
- Docker support with multi-stage build
- Docker Compose configuration with external network support
- Comprehensive documentation:
  - README.md with full feature documentation
  - SETUP_WINDOWS.md with step-by-step Windows setup guide
  - QUICKSTART.md for rapid deployment
- Setup scripts for Linux (setup.sh) and Windows (setup.bat)
- Example configuration files:
  - .env.example for environment variables
  - claude_desktop_config.json for Claude Desktop
- Health check endpoint for container monitoring
- Environment-based configuration
- Graceful error handling and informative error messages

### Configuration
- Default DX Cluster: dxc.nc7j.com:7373 (NC7J)
- Default port: 8000 (SSE transport)
- External network: ea1rfi-network
- Configurable callsign, cluster host, port, and API key

### Security
- API Key authentication via Authorization header
- Bearer token support
- X-API-Key header support
- Environment variable for sensitive configuration

### Documentation
- Complete setup guide for Windows with MCP Proxy
- Troubleshooting section with common issues
- Security best practices
- Docker deployment instructions
- Claude Desktop integration guide
- Example usage prompts

## [Unreleased]

### Planned Features
- Web UI for server management
- Support for multiple DX Clusters simultaneously
- Spot caching and database storage
- Real-time spot streaming via WebSocket
- Advanced filtering (QSL info, continent, etc.)
- Integration with QRZ.com and HamQTH APIs
- Call book lookup integration
- Propagation prediction integration
- Alert notifications for specific calls/countries
- Statistics dashboard
- Historical spot analysis
- Export spots to ADIF format
- Support for DX Summit protocol

### Future Enhancements
- OAuth2 authentication option
- Rate limiting
- Multi-user support with user-specific filters
- Prometheus metrics endpoint
- Grafana dashboard templates
- Kubernetes deployment manifests
- CI/CD pipeline
- Automated testing suite
- Performance optimizations

---

For more information, see [README.md](README.md).
