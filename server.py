"""
DX Cluster MCP Server
A FastMCP-based server for Ham Radio DX Cluster operations with SSE transport and API Key authentication.
"""

import os
import asyncio
import telnetlib3
from datetime import datetime
from typing import Optional, List, Dict, Any
import re
from collections import defaultdict

from fastmcp import FastMCP


# Configuration from environment variables
DX_CLUSTER_HOST = os.getenv("DX_CLUSTER_HOST", "dxc.nc7j.com")
DX_CLUSTER_PORT = int(os.getenv("DX_CLUSTER_PORT", "7373"))
CALLSIGN = os.getenv("CALLSIGN", "N0CALL")
API_KEY = os.getenv("API_KEY", "your-secure-api-key-here")

# Initialize FastMCP server
mcp = FastMCP("DX Cluster Server")


class DXClusterConnection:
    """Manages connection to DX Cluster via telnet"""

    def __init__(self, host: str, port: int, callsign: str):
        self.host = host
        self.port = port
        self.callsign = callsign
        self.reader = None
        self.writer = None
        self.connected = False
        self.spots_cache = []
        self.max_cache_size = 1000

    async def connect(self):
        """Establish telnet connection to DX Cluster"""
        try:
            self.reader, self.writer = await telnetlib3.open_connection(
                self.host,
                self.port,
                connect_minwait=2.0
            )
            self.connected = True

            # Wait for login prompt and send callsign
            await asyncio.sleep(1)
            await self._read_until_prompt()
            self.writer.write(f"{self.callsign}\n")
            await asyncio.sleep(1)
            await self._read_until_prompt()

            return True
        except Exception as e:
            self.connected = False
            raise Exception(f"Failed to connect to DX Cluster: {str(e)}")

    async def _read_until_prompt(self, timeout: float = 5.0) -> str:
        """Read data until a prompt or timeout"""
        data = ""
        try:
            start_time = asyncio.get_event_loop().time()
            while True:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    break

                chunk = await asyncio.wait_for(self.reader.read(4096), timeout=0.5)
                if chunk:
                    data += chunk
                else:
                    break
        except asyncio.TimeoutError:
            pass

        return data

    async def send_command(self, command: str, wait_time: float = 2.0) -> str:
        """Send command to DX Cluster and return response"""
        if not self.connected:
            await self.connect()

        try:
            self.writer.write(f"{command}\n")
            await asyncio.sleep(wait_time)
            response = await self._read_until_prompt()
            return response
        except Exception as e:
            self.connected = False
            raise Exception(f"Failed to send command: {str(e)}")

    async def disconnect(self):
        """Close connection to DX Cluster"""
        if self.writer:
            self.writer.write("bye\n")
            await asyncio.sleep(0.5)
            self.writer.close()
        self.connected = False

    def parse_spot(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a DX spot line into structured data"""
        # DX spot format: DX de CALL:     FREQ  DXCALL       Comment                 TIME Z
        # Example: DX de W1AW:     14.074  EA1RFI       FT8 Signal                1234Z
        pattern = r'DX de ([A-Z0-9/-]+):\s+([0-9.]+)\s+([A-Z0-9/-]+)\s+(.+?)\s+(\d{4})Z'
        match = re.match(pattern, line.strip())

        if match:
            spotter, freq, dx_call, comment, time = match.groups()
            return {
                "spotter": spotter,
                "frequency": float(freq),
                "dx_callsign": dx_call,
                "comment": comment.strip(),
                "time": time,
                "timestamp": datetime.utcnow().isoformat(),
                "raw": line.strip()
            }
        return None


# Global connection instance
dx_connection = DXClusterConnection(DX_CLUSTER_HOST, DX_CLUSTER_PORT, CALLSIGN)


@mcp.tool()
async def read_spots(count: int = 10, band: Optional[str] = None,
                     callsign: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Read recent DX spots from the cluster.

    Args:
        count: Number of spots to retrieve (default: 10, max: 100)
        band: Optional band filter (e.g., "20m", "40m", "15m")
        callsign: Optional callsign filter to search for specific station

    Returns:
        List of DX spots with details including frequency, callsign, spotter, time, and comments
    """
    if count > 100:
        count = 100

    try:
        # Build command based on filters
        if callsign:
            command = f"sh/dx {count} {callsign}"
        elif band:
            command = f"sh/dx {count} on {band}"
        else:
            command = f"sh/dx {count}"

        response = await dx_connection.send_command(command, wait_time=3.0)

        # Parse spots from response
        spots = []
        for line in response.split('\n'):
            if line.strip().startswith('DX de'):
                spot = dx_connection.parse_spot(line)
                if spot:
                    spots.append(spot)

        return spots

    except Exception as e:
        raise ValueError(f"Failed to read spots: {str(e)}")


@mcp.tool()
async def post_spot(frequency: float, dx_callsign: str, comment: str = "") -> Dict[str, str]:
    """
    Post a DX spot to the cluster.

    Args:
        frequency: Frequency in MHz (e.g., 14.074 for 20m FT8)
        dx_callsign: Callsign of the station being spotted
        comment: Optional comment about the spot (mode, signal report, etc.)

    Returns:
        Confirmation message with spot details
    """
    try:
        # Validate frequency (should be between 1.8 and 30 MHz for HF)
        if not (1.8 <= frequency <= 450.0):
            raise ValueError("Frequency must be between 1.8 and 450.0 MHz")

        # Validate callsign format (basic check)
        if not re.match(r'^[A-Z0-9/-]+$', dx_callsign.upper()):
            raise ValueError("Invalid callsign format")

        # Build DX command
        command = f"dx {frequency} {dx_callsign.upper()}"
        if comment:
            command += f" {comment}"

        response = await dx_connection.send_command(command, wait_time=2.0)

        return {
            "status": "success",
            "frequency": str(frequency),
            "dx_callsign": dx_callsign.upper(),
            "comment": comment,
            "response": response.strip()
        }

    except Exception as e:
        raise ValueError(f"Failed to post spot: {str(e)}")


@mcp.tool()
async def analyze_spots(hours: int = 1, analysis_type: str = "summary") -> Dict[str, Any]:
    """
    Analyze DX spots to provide insights and statistics.

    Args:
        hours: Number of hours to analyze (default: 1, max: 24)
        analysis_type: Type of analysis - "summary", "bands", "countries", or "modes"

    Returns:
        Analysis results with statistics and insights
    """
    if hours > 24:
        hours = 24

    try:
        # Get spots for analysis
        spots_to_analyze = 50 if hours == 1 else min(hours * 50, 500)
        response = await dx_connection.send_command(f"sh/dx {spots_to_analyze}", wait_time=4.0)

        # Parse all spots
        spots = []
        for line in response.split('\n'):
            if line.strip().startswith('DX de'):
                spot = dx_connection.parse_spot(line)
                if spot:
                    spots.append(spot)

        if not spots:
            return {"error": "No spots available for analysis"}

        # Perform analysis based on type
        if analysis_type == "summary":
            return {
                "total_spots": len(spots),
                "unique_spotters": len(set(s["spotter"] for s in spots)),
                "unique_dx_stations": len(set(s["dx_callsign"] for s in spots)),
                "frequency_range": {
                    "min": min(s["frequency"] for s in spots),
                    "max": max(s["frequency"] for s in spots)
                },
                "most_spotted": _get_most_common([s["dx_callsign"] for s in spots], 5),
                "most_active_spotters": _get_most_common([s["spotter"] for s in spots], 5)
            }

        elif analysis_type == "bands":
            band_counts = defaultdict(int)
            for spot in spots:
                band = _frequency_to_band(spot["frequency"])
                band_counts[band] += 1

            return {
                "total_spots": len(spots),
                "spots_per_band": dict(sorted(band_counts.items(),
                                             key=lambda x: x[1], reverse=True))
            }

        elif analysis_type == "countries":
            country_counts = defaultdict(int)
            for spot in spots:
                # Extract country prefix (simplified)
                prefix = _extract_country_prefix(spot["dx_callsign"])
                country_counts[prefix] += 1

            return {
                "total_spots": len(spots),
                "spots_per_country_prefix": dict(sorted(country_counts.items(),
                                                       key=lambda x: x[1], reverse=True)[:20])
            }

        elif analysis_type == "modes":
            mode_counts = defaultdict(int)
            for spot in spots:
                mode = _extract_mode_from_comment(spot["comment"])
                mode_counts[mode] += 1

            return {
                "total_spots": len(spots),
                "spots_per_mode": dict(sorted(mode_counts.items(),
                                             key=lambda x: x[1], reverse=True))
            }

        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")

    except Exception as e:
        raise ValueError(f"Failed to analyze spots: {str(e)}")


@mcp.tool()
async def check_connection() -> Dict[str, Any]:
    """
    Check the connection status to the DX Cluster.

    Returns:
        Connection status, cluster info, and configuration
    """
    try:
        if not dx_connection.connected:
            await dx_connection.connect()

        # Try to get cluster info
        response = await dx_connection.send_command("sh/node", wait_time=2.0)

        return {
            "status": "connected",
            "cluster_host": DX_CLUSTER_HOST,
            "cluster_port": DX_CLUSTER_PORT,
            "callsign": CALLSIGN,
            "cluster_info": response.strip()[:500]  # Limit response size
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "cluster_host": DX_CLUSTER_HOST,
            "cluster_port": DX_CLUSTER_PORT,
            "callsign": CALLSIGN
        }


def _get_most_common(items: List[str], count: int) -> List[Dict[str, Any]]:
    """Get most common items with counts"""
    counts = defaultdict(int)
    for item in items:
        counts[item] += 1

    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"value": k, "count": v} for k, v in sorted_items[:count]]


def _frequency_to_band(freq: float) -> str:
    """Convert frequency to ham band"""
    if 1.8 <= freq < 2.0:
        return "160m"
    elif 3.5 <= freq < 4.0:
        return "80m"
    elif 7.0 <= freq < 7.3:
        return "40m"
    elif 10.1 <= freq < 10.15:
        return "30m"
    elif 14.0 <= freq < 14.35:
        return "20m"
    elif 18.068 <= freq < 18.168:
        return "17m"
    elif 21.0 <= freq < 21.45:
        return "15m"
    elif 24.89 <= freq < 24.99:
        return "12m"
    elif 28.0 <= freq < 29.7:
        return "10m"
    elif 50.0 <= freq < 54.0:
        return "6m"
    elif 144.0 <= freq < 148.0:
        return "2m"
    else:
        return f"{freq:.3f}MHz"


def _extract_country_prefix(callsign: str) -> str:
    """Extract country prefix from callsign (simplified)"""
    # Remove /P, /M, /QRP suffixes
    base_call = callsign.split('/')[0]

    # Get prefix (letters and first digit)
    match = re.match(r'^([A-Z0-9]+?)(\d)', base_call)
    if match:
        return match.group(1) + match.group(2)
    return base_call[:2]


def _extract_mode_from_comment(comment: str) -> str:
    """Extract operating mode from comment"""
    comment_upper = comment.upper()
    modes = ["CW", "SSB", "FT8", "FT4", "RTTY", "PSK31", "JT65", "JT9", "DIGI", "PSK", "MFSK"]

    for mode in modes:
        if mode in comment_upper:
            return mode

    return "UNKNOWN"


# Middleware for API Key authentication
@mcp.add_middleware
async def authenticate(request, call_next):
    """Verify API Key in Authorization header"""
    # For SSE transport, check authorization header
    if hasattr(request, 'headers'):
        auth_header = request.headers.get('Authorization', '')

        # Check for Bearer token
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            if token == API_KEY:
                return await call_next(request)

        # Check for simple API key in header
        api_key_header = request.headers.get('X-API-Key', '')
        if api_key_header == API_KEY:
            return await call_next(request)

        return {"error": "Unauthorized", "message": "Invalid API Key"}, 401

    # Allow the request to proceed if no headers (local/stdio mode)
    return await call_next(request)


if __name__ == "__main__":
    # Run with SSE transport
    # The API key will be validated via middleware
    print(f"Starting DX Cluster MCP Server")
    print(f"Cluster: {DX_CLUSTER_HOST}:{DX_CLUSTER_PORT}")
    print(f"Callsign: {CALLSIGN}")
    print(f"API Key authentication: {'Enabled' if API_KEY != 'your-secure-api-key-here' else 'DISABLED (SET API_KEY!)'}")

    mcp.run(transport="sse", host="0.0.0.0", port=8000)
