# weather-mcp

Production-grade scaffold for a Weather MCP Server built with Python 3.11, FastMCP, Pydantic v2, httpx, SQLite, uv, Docker, `.env` configuration, and structured logging.

> This repository intentionally contains infrastructure and data models only. It does not implement business logic, outbound API requests, or MCP tools.

## Directory structure

```text
weather-mcp/
├── .gitignore
├── Dockerfile
├── README.md
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── src/
    └── weather_mcp/
        ├── __init__.py
        ├── config.py
        ├── logger.py
        ├── models.py
        └── settings.py
```

## Requirements

- Python 3.11
- uv
- Docker and Docker Compose, for containerized execution

## Local setup

```bash
uv venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Create a local `.env` file as needed:

```dotenv
WEATHER_MCP_APP_NAME=weather-mcp
WEATHER_MCP_ENVIRONMENT=local
WEATHER_MCP_LOG_LEVEL=INFO
WEATHER_MCP_DATABASE_URL=sqlite:///data/weather_mcp.db
```

## Quality checks

```bash
uv run ruff check .
uv run black --check .
uv run mypy
```

## Docker

```bash
docker compose up --build
```

The compose stack persists SQLite data in the `weather_mcp_data` Docker volume.
