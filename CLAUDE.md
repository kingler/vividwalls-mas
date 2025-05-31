# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VividMAS (Self-hosted AI Package) is a comprehensive Docker-based Local AI development platform that combines multiple AI and automation tools into a unified stack. It's based on n8n's self-hosted AI starter kit with additional enhancements including Supabase, Open WebUI, Flowise, Langfuse, SearXNG, and Caddy.

## Architecture

The platform consists of multiple interconnected services:

### Core Services

- **n8n** (localhost:5678): Low-code workflow automation platform with 400+ integrations
- **Open WebUI** (localhost:3000): ChatGPT-like interface for interacting with local LLMs and n8n agents
- **Flowise** (localhost:3001): No-code AI agent builder that pairs with n8n
- **Supabase** (localhost:8000): Database-as-a-service with authentication and vector storage
- **Ollama** (localhost:11434): Local LLM server for running models like Qwen2.5
- **Langfuse** (localhost:3002): LLM observability and monitoring platform

### Supporting Services
- **Qdrant** (localhost:6333): High-performance vector database
- **SearXNG** (localhost:8080): Privacy-focused metasearch engine
- **Caddy**: Reverse proxy with automatic HTTPS/TLS for production deployments
- **PostgreSQL**: Primary database (exposed on localhost:5433 for external access)
- **Redis/Valkey**: Caching and session management
- **ClickHouse**: Analytics database for Langfuse
- **MinIO** (localhost:9090): S3-compatible object storage

## Development Commands

### Starting Services

Use the `start_services.py` script to start all services:

```bash
# For CPU-only (Mac/Apple Silicon users)
python start_services.py --profile cpu

# For NVIDIA GPU users
python start_services.py --profile gpu-nvidia

# For AMD GPU users (Linux)
python start_services.py --profile gpu-amd

# For external Ollama (Mac users running Ollama locally)
python start_services.py --profile none
```

### Service Management

```bash
# Stop all services
docker compose -p localai -f docker-compose.yml --profile <profile> down

# View service status
docker ps

# View logs for specific service
docker compose -p localai logs -f <service-name>

# Update containers to latest versions
docker compose -p localai -f docker-compose.yml --profile <profile> pull
```

### Configuration Files

- `.env`: Main environment configuration (copy from `env.example`)
- `docker-compose.yml`: Main service orchestration
- `supabase/docker/docker-compose.yml`: Supabase-specific services
- `Caddyfile`: Reverse proxy configuration for production
- `searxng/settings.yml`: SearXNG search engine configuration

## Important Development Notes

### Environment Setup

1. Copy `.env.example` to `.env` and configure required secrets
2. Generate secure random values for all JWT secrets and encryption keys
3. For production deployment, configure hostname variables for Caddy SSL

### Mac Users with Local Ollama

If running Ollama locally on Mac (not in Docker):
1. Set `OLLAMA_HOST=host.docker.internal:11434` in docker-compose.yml
2. In n8n credentials, use base URL: `http://host.docker.internal:11434/`

### Internal Service URLs

When configuring service connections within the Docker network:
- Ollama: `http://ollama:11434`
- PostgreSQL: `db:5432` (username: postgres, password from .env)
- Qdrant: `http://qdrant:6333`
- SearXNG: `http://searxng:8080`

### File Access

The `./shared` directory is mounted to `/data/shared` inside the n8n container for local file operations.

## Deployment

### Local Development
Use `start_services.py` with appropriate GPU profile

### Production (Digital Ocean)
1. Use `deploy-to-digitalocean.sh` script for automated deployment
2. Configure DNS A records for all subdomains
3. Caddy handles SSL certificate generation automatically

## Troubleshooting

### Common Issues

- **Supabase Pooler Restarting**: Check PostgreSQL password doesn't contain "@" character
- **SearXNG First Run**: Script automatically handles cap_drop modifications for initial setup
- **GPU Support**: Ensure Docker has GPU access configured per platform
- **Memory Issues**: Supabase analytics may fail if PostgreSQL password changed - delete `supabase/docker/volumes/db/data`

### Log Locations
- Application logs: `docker compose -p localai logs <service>`
- Service-specific issues: Check individual container logs
- SearXNG secret key generation: Handled automatically by `start_services.py`