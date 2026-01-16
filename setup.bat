@echo off
REM DX Cluster MCP Server Setup Script for Windows

echo ==========================================
echo DX Cluster MCP Server Setup
echo ==========================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo WARNING: Please edit .env file with your callsign and API key!
    echo.
)

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if docker-compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: docker-compose is not installed. Please install docker-compose first.
    pause
    exit /b 1
)

echo Docker and docker-compose are installed
echo.

REM Create external network if it doesn't exist
set NETWORK_NAME=ea1rfi-network
docker network ls | findstr %NETWORK_NAME% >nul 2>&1
if errorlevel 1 (
    echo Creating external network: %NETWORK_NAME%...
    docker network create %NETWORK_NAME%
    echo Network created successfully
) else (
    echo Network '%NETWORK_NAME%' already exists
)
echo.

REM Build and start the server
echo Building and starting DX Cluster MCP Server...
docker-compose up -d --build

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Server is running at: http://localhost:8000
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
echo To stop the server:
echo   docker-compose down
echo.
echo WARNING: Don't forget to:
echo   1. Edit .env with your callsign and secure API key
echo   2. Configure Claude Desktop with the provided configuration
echo   3. Restart the server: docker-compose restart
echo.
echo 73!
echo.
pause
