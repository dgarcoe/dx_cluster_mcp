#!/bin/bash

# DX Cluster MCP Server Setup Script

set -e

echo "=========================================="
echo "DX Cluster MCP Server Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your callsign and API key!"
    echo ""
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "✅ Docker and docker-compose are installed"
echo ""

# Create external network if it doesn't exist
NETWORK_NAME="ea1rfi-network"
if ! docker network ls | grep -q $NETWORK_NAME; then
    echo "Creating external network: $NETWORK_NAME..."
    docker network create $NETWORK_NAME
    echo "✅ Network created successfully"
else
    echo "✅ Network '$NETWORK_NAME' already exists"
fi
echo ""

# Build and start the server
echo "Building and starting DX Cluster MCP Server..."
docker-compose up -d --build

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Server is running at: http://localhost:8000"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the server:"
echo "  docker-compose down"
echo ""
echo "⚠️  Don't forget to:"
echo "  1. Edit .env with your callsign and secure API key"
echo "  2. Configure Claude Desktop with the provided configuration"
echo "  3. Restart the server: docker-compose restart"
echo ""
echo "73!"
