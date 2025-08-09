# Technical Stack

## Application Framework

- **Framework:** Python
- **Version:** 3.10+

## Database

- **Primary Database:** n/a (API client, no database)

## JavaScript

- **Framework:** n/a
- **Import Strategy:** n/a

## Package Manager

- **Tool:** pip/uv
- **Lock File:** requirements.txt

## Python Framework

- **Async Framework:** asyncio
- **Web Framework:** n/a (MCP server protocol)

## API Client

- **GitLab Client:** python-gitlab 4.0.0+
- **Protocol:** MCP (Model Context Protocol) 0.1.0+

## Data Validation

- **Library:** pydantic 2.0.0+

## Testing Framework

- **Framework:** pytest 7.0.0+
- **Async Testing:** pytest-asyncio 0.21.0+
- **Coverage:** pytest-cov 4.0.0+
- **Mocking:** pytest-mock 3.10.0+

## Logging

- **JSON Logger:** python-json-logger 2.0.0+
- **Structured Logging:** Yes

## Environment Management

- **Config:** python-dotenv 1.0.0+

## Build System

- **Build Backend:** hatchling
- **Package Manager:** pip/uv

## Development Tools

- **Type Checking:** Python type hints
- **Code Style:** Python conventions

## Application Hosting

- **Deployment Model:** Local process (stdio-based MCP server)
- **Client Integration:** Claude Desktop, Cline, other MCP clients

## Code Repository

- **Repository URL:** https://github.com/vafakaramzadegan/mcp-gitlab