#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.yml"
DEPLOY_COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.deploy.yml"
MODE="${1:-dev}"

web_pid=""

ensure_env_file() {
  if [ ! -f "$ROOT_DIR/.env" ]; then
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    echo "Created .env from .env.example"
  fi
}

load_env_defaults() {
  local env_file="$ROOT_DIR/.env"
  [ -f "$env_file" ] || return 0

  local line key value
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%$'\r'}"
    case "$line" in
      ''|\#*) continue
        ;;
    esac

    key="${line%%=*}"
    value="${line#*=}"

    if [ -z "${!key:-}" ]; then
      export "$key=$value"
    fi
  done < "$env_file"
}

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing command: $1"
    exit 1
  fi
}

has_docker_compose() {
  command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1
}

compose_dev() {
  docker compose --env-file "$ROOT_DIR/.env" -f "$DEV_COMPOSE_FILE" "$@"
}

compose_deploy() {
  docker compose --env-file "$ROOT_DIR/.env" -f "$DEPLOY_COMPOSE_FILE" "$@"
}

wait_for_container_health() {
  local service="$1"
  local attempts="${2:-60}"
  local container_id=""
  local health_status=""

  echo "Waiting for ${service} to become healthy..."
  for _ in $(seq 1 "$attempts"); do
    container_id="$(compose_dev ps -q "$service" 2>/dev/null || true)"
    if [ -n "$container_id" ]; then
      health_status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id" 2>/dev/null || true)"
      if [ "$health_status" = "healthy" ] || [ "$health_status" = "running" ]; then
        return
      fi
    fi
    sleep 1
  done

  echo "${service} did not become ready in time."
  exit 1
}

wait_for_http() {
  local url="$1"
  local attempts="${2:-60}"

  need_cmd curl

  echo "Waiting for ${url}"
  for _ in $(seq 1 "$attempts"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return
    fi
    sleep 1
  done

  echo "Service did not become ready: ${url}"
  exit 1
}

ensure_web_deps() {
  need_cmd pnpm

  if [ ! -d "$ROOT_DIR/apps/web/node_modules" ]; then
    echo "Installing web dependencies..."
    (cd "$ROOT_DIR/apps/web" && pnpm install)
  fi
}

cleanup_local_processes() {
  if [ -n "$web_pid" ] && kill -0 "$web_pid" >/dev/null 2>&1; then
    kill "$web_pid" >/dev/null 2>&1 || true
  fi
}

usage() {
  cat <<EOF
Usage:
  ./start.sh              Start backend in Docker and web locally
  ./start.sh dev          Same as default
  ./start.sh deps         Start backend in Docker only
  ./start.sh down         Stop backend in Docker
  ./start.sh docker       Start the full stack in Docker
  ./start.sh docker-down  Stop the full stack in Docker
  ./start.sh help         Show this message
EOF
}

ensure_env_file
load_env_defaults

API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-3000}"
POSTGRES_PORT="${POSTGRES_PORT:-5436}"
POSTGRES_DB="${POSTGRES_DB:-app}"
POSTGRES_USER="${POSTGRES_USER:-app}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-app}"
API_ORIGIN="${API_ORIGIN:-http://localhost:${API_PORT}}"
WEB_ORIGIN="${WEB_ORIGIN:-http://localhost:${WEB_PORT}}"
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-${API_ORIGIN}/api}"
CORS_ORIGINS="${CORS_ORIGINS:-[\"${WEB_ORIGIN}\"]}"
SEED_ADMIN="${SEED_ADMIN:-1}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@example.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123456}"
ADMIN_FULL_NAME="${ADMIN_FULL_NAME:-Template Admin}"

export API_PORT WEB_PORT POSTGRES_PORT
export POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD
export API_ORIGIN WEB_ORIGIN NEXT_PUBLIC_API_URL CORS_ORIGINS
export SEED_ADMIN ADMIN_EMAIL ADMIN_PASSWORD ADMIN_FULL_NAME

run_api_startup_tasks_dev() {
  echo "Ensuring database schema and initial data are ready..."
  compose_dev exec -T \
    -e SEED_ADMIN="$SEED_ADMIN" \
    -e ADMIN_EMAIL="$ADMIN_EMAIL" \
    -e ADMIN_PASSWORD="$ADMIN_PASSWORD" \
    -e ADMIN_FULL_NAME="$ADMIN_FULL_NAME" \
    api python -m app.core.migrate
}

run_api_startup_tasks_deploy() {
  echo "Ensuring database schema and initial data are ready..."
  compose_deploy exec -T \
    -e SEED_ADMIN="$SEED_ADMIN" \
    -e ADMIN_EMAIL="$ADMIN_EMAIL" \
    -e ADMIN_PASSWORD="$ADMIN_PASSWORD" \
    -e ADMIN_FULL_NAME="$ADMIN_FULL_NAME" \
    api python -m app.core.migrate
}

start_dev_dependencies() {
  if ! has_docker_compose; then
    echo "Docker Compose not found."
    exit 1
  fi

  echo "Starting backend in Docker..."
  compose_dev up -d --build postgres api
  wait_for_container_health postgres 60
  wait_for_http "${API_ORIGIN}/healthz" 90
  run_api_startup_tasks_dev
}

start_web() {
  ensure_web_deps

  echo "Starting web on http://localhost:${WEB_PORT}"
  (
    cd "$ROOT_DIR/apps/web"
    NEXT_PUBLIC_API_URL="$NEXT_PUBLIC_API_URL" pnpm dev --hostname 0.0.0.0 --port "$WEB_PORT"
  ) &
  web_pid=$!
}

start_dev() {
  trap cleanup_local_processes INT TERM EXIT

  start_dev_dependencies
  start_web

  echo ""
  echo "Project is running:"
  echo "  Web: http://localhost:${WEB_PORT}"
  echo "  API: http://localhost:${API_PORT}/docs"
  echo "  Database: PostgreSQL via Docker on localhost:${POSTGRES_PORT}"
  echo "Press Ctrl+C to stop the local web server."
  echo "Run ./start.sh down to stop Docker backend services."

  wait
}

stop_dev_dependencies() {
  need_cmd docker
  ensure_env_file
  compose_dev down
}

start_full_docker() {
  need_cmd docker
  ensure_env_file

  echo "Starting full stack in Docker..."
  compose_deploy up -d --build
  wait_for_http "${API_ORIGIN}/healthz" 90
  run_api_startup_tasks_deploy

  echo ""
  echo "Project is running in Docker:"
  echo "  Web: http://localhost:${WEB_PORT}"
  echo "  API: http://localhost:${API_PORT}/docs"
}

stop_full_docker() {
  need_cmd docker
  ensure_env_file
  compose_deploy down
}

case "$MODE" in
  dev)
    start_dev
    ;;
  deps)
    need_cmd docker
    start_dev_dependencies
    ;;
  down)
    stop_dev_dependencies
    ;;
  docker)
    start_full_docker
    ;;
  docker-down)
    stop_full_docker
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    usage
    exit 1
    ;;
esac
