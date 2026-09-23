# MoneyGraph Docker deployment

This deployment runs the existing MoneyGraph application on a small Ubuntu VPS:

```text
Internet
  -> nginx :80
     -> /       -> frontend:3000
     -> /api/   -> backend:8000
     -> /health -> backend:8000
```

The stack contains only the FastAPI backend, Next.js frontend, and Nginx reverse proxy. It has no database or Redis. The backend image includes the organizer parquet inputs and generated CSV findings, so no runtime data volume is required.

## VPS preparation

Install Docker Engine with the Docker Compose plugin using Docker's instructions for your Ubuntu release. Allow inbound TCP port 80 in the VPS firewall or security group.

A frontend production build can briefly exceed the comfortable memory available on a 1 GB VPS. Configure 2 GB of swap before building:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Run `swapon --show` to verify it. Add the `/etc/fstab` entry only once.

## Build and start

Run these commands from the repository root:

```bash
cp .env.example .env
# set OPENAI_API_KEY if desired
docker compose -f infra/docker-compose.yml build
docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml ps
curl http://localhost/health
```

Open `http://SERVER_IP/` in a browser. Nginx serves the frontend and forwards same-origin `/api/...` requests to FastAPI without changing their paths.

The deterministic analysis results, API, and frontend work without an OpenAI key. `OPENAI_API_KEY` and `OPENAI_MODEL` are read from the runtime environment by Docker Compose and passed only to the backend container. They are not Docker build arguments and are never included in the frontend image or browser bundle. Leave `OPENAI_API_KEY` empty when the optional investigator is not needed.

The backend image uses the generated files currently stored in `output/`. Run `make analyze` before rebuilding whenever the parquet inputs or deterministic configuration change.

## Operations

View all logs:

```bash
docker compose -f infra/docker-compose.yml logs -f --tail=100
```

View one service:

```bash
docker compose -f infra/docker-compose.yml logs -f --tail=100 backend
```

Restart the stack:

```bash
docker compose -f infra/docker-compose.yml restart
```

Stop and remove the containers and network:

```bash
docker compose -f infra/docker-compose.yml down
```

Rebuild after pulling a new repository version:

```bash
docker compose -f infra/docker-compose.yml build
docker compose -f infra/docker-compose.yml up -d
```

The containers use `restart: unless-stopped`, which is appropriate for a demo VPS and restores the services after a host reboot when Docker starts.
