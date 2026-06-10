# Full Stack Admin Template

一个面向 AI/后台管理类项目的全栈快速开发模板。

## Stack

- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS v4, lucide-react, sonner, pnpm
- Backend: FastAPI, Pydantic Settings, SQLAlchemy 2.x, Alembic, uv, pytest
- Infra: Docker Compose, PostgreSQL, storage volume, healthcheck, one-command start script

## Quick Start

```bash
cp .env.example .env
bash start.sh
```

Default behavior:

- Start PostgreSQL and API with Docker Compose
- Start Web locally with hot reload

Open:

- Web: `http://localhost:${WEB_PORT}`
- API: `http://localhost:${API_PORT}/docs`
- Healthcheck: `http://localhost:${API_PORT}/healthz`

Default admin:

- Username: `admin`
- Password: `admin123456`

## Local Development Without Docker

Run API locally only when needed:

```bash
cd apps/api
uv sync
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

Web:

```bash
cd apps/web
pnpm install
pnpm dev
```

Standard startup:

```bash
bash start.sh
```

Useful commands:

```bash
 bash start.sh deps        # start PostgreSQL and API in Docker
 bash start.sh down        # stop PostgreSQL and API in Docker
 bash start.sh docker      # start the full stack in Docker
 bash start.sh docker-down # stop the full stack in Docker
```

Common port variables in `.env`:

```bash
API_PORT=8000
WEB_PORT=3000
POSTGRES_PORT=5436
API_ORIGIN=http://localhost:8000
WEB_ORIGIN=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Structure

```text
apps/
  api/
    app/
      core/
      auth/
      users/
      tasks/
      assets/
      main.py
      models.py
      roles.py
    migrations/
    tests/
  web/
    app/
    src/
infra/
storage/
docs/
```

## Notes

- `apps/api/app/roles.py` seeds permissions, the admin role, and the default admin user.
- SQLite is used by default for lightweight local API development.
- `start.sh` defaults to starting the backend in Docker while Web runs locally.
- `deploy/docker-compose.yml` is for development backend services.
- `deploy/docker-compose.deploy.yml` is for running the full stack in Docker.
- Docker Compose uses PostgreSQL and mounts `storage/` as the file volume.
- Tailwind CSS v4 configuration lives in `apps/web/app/globals.css`.
