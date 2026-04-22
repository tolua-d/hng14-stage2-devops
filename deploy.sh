#!/usr/bin/env bash
# =============================================================================
# rolling_deploy.sh
#
# Performs a zero-downtime rolling update for one service at a time.
# The new container must pass its Docker HEALTHCHECK within HEALTH_TIMEOUT
# seconds before the old container is stopped.  If it does not, the old
# container is left running and the script exits non-zero.
#
# Usage:
#   ./scripts/rolling_deploy.sh <service> <new_image>
#
# Example (called by GitHub Actions):
#   ./scripts/rolling_deploy.sh api hng-api:abc1234
#   ./scripts/rolling_deploy.sh worker hng-worker:abc1234
#   ./scripts/rolling_deploy.sh frontend hng-frontend:abc1234
#
# Environment variables (set in the deployment environment):
#   COMPOSE_FILE   Path to docker-compose.yml  (default: docker-compose.yml)
#   HEALTH_TIMEOUT Maximum seconds to wait for new container to become healthy
#                  (default: 60)
# =============================================================================
set -euo pipefail

SERVICE="${1:?Usage: $0 <service> <new_image>}"
NEW_IMAGE="${2:?Usage: $0 <service> <new_image>}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-60}"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-hng14}"

log()  { echo "[$(date '+%H:%M:%S')] $*"; }
fail() { echo "[$(date '+%H:%M:%S')] ERROR: $*" >&2; exit 1; }

# ── 0. Verify the compose file exists ────────────────────────────────────────
[[ -f "$COMPOSE_FILE" ]] || fail "Compose file not found: $COMPOSE_FILE"

# ── 1. Find the currently running container for this service ──────────────────
log "Looking for running container for service '$SERVICE' ..."
OLD_CONTAINER=$(
  docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" \
    ps -q "$SERVICE" 2>/dev/null | head -1
)

if [[ -z "$OLD_CONTAINER" ]]; then
  log "No existing container found — performing a fresh start instead."
  docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" \
    up -d --no-deps "$SERVICE"
  exit 0
fi

log "Old container: $OLD_CONTAINER"

# ── 2. Pull / tag the new image ───────────────────────────────────────────────
log "Pulling new image: $NEW_IMAGE ..."
docker pull "$NEW_IMAGE" || fail "Failed to pull $NEW_IMAGE"

# ── 3. Start the new container (scale to 2 briefly) ──────────────────────────
log "Starting new container for '$SERVICE' alongside the old one ..."
IMAGE_TAG="${NEW_IMAGE##*:}" \
  docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" \
    up -d --no-deps --no-recreate --scale "${SERVICE}=2" "$SERVICE" 2>/dev/null || true

# Get the ID of the newest container (highest creation time)
NEW_CONTAINER=$(
  docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" \
    ps -q "$SERVICE" | grep -v "^${OLD_CONTAINER}$" | head -1
)

if [[ -z "$NEW_CONTAINER" ]]; then
  fail "Could not identify the new container. Aborting — old container still running."
fi

log "New container: $NEW_CONTAINER"

# ── 4. Wait for the new container's HEALTHCHECK to pass ──────────────────────
log "Waiting up to ${HEALTH_TIMEOUT}s for new container to become healthy ..."
elapsed=0
while true; do
  health=$(docker inspect --format='{{.State.Health.Status}}' "$NEW_CONTAINER" 2>/dev/null || echo "unknown")

  if [[ "$health" == "healthy" ]]; then
    log "New container is healthy."
    break
  fi

  if (( elapsed >= HEALTH_TIMEOUT )); then
    log "Health check timed out after ${HEALTH_TIMEOUT}s (status: $health)."
    log "Stopping and removing the new container — old container remains running."
    docker stop "$NEW_CONTAINER" && docker rm "$NEW_CONTAINER" || true
    fail "Rolling deploy aborted. '$SERVICE' was NOT updated."
  fi

  sleep 2
  (( elapsed += 2 ))
done

# ── 5. Stop and remove the old container ─────────────────────────────────────
log "Stopping old container $OLD_CONTAINER ..."
docker stop "$OLD_CONTAINER"
docker rm   "$OLD_CONTAINER"
log "Old container removed."

# ── 6. Confirm final state ────────────────────────────────────────────────────
log "Final container status for '$SERVICE':"
docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps "$SERVICE"

log "Rolling deploy of '$SERVICE' → $NEW_IMAGE completed successfully."