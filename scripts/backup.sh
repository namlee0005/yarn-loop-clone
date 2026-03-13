#!/usr/bin/env bash
# =============================================================================
# backup.sh — Automated PostgreSQL backup for Yarn Loop (T-029)
#
# Usage:
#   ./scripts/backup.sh
#
# Env vars (override via .env or CI secrets):
#   PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
#   BACKUP_DIR      — local directory for dumps   (default: ./backups)
#   RETAIN_DAYS     — days to keep old backups    (default: 7)
#
# Cron example (daily at 02:00):
#   0 2 * * * /path/to/project/scripts/backup.sh >> /var/log/yarn-loop-backup.log 2>&1
# =============================================================================

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-yarnloop}"
BACKUP_DIR="${BACKUP_DIR:-$(dirname "$0")/../backups}"
RETAIN_DAYS="${RETAIN_DAYS:-7}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/yarnloop_${TIMESTAMP}.dump"

# ── Preflight ─────────────────────────────────────────────────────────────────
if ! command -v pg_dump &>/dev/null; then
  echo "[ERROR] pg_dump not found. Install postgresql-client." >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"

# ── Dump ──────────────────────────────────────────────────────────────────────
echo "[INFO] $(date -u +"%Y-%m-%dT%H:%M:%SZ") — Starting backup: ${BACKUP_FILE}"

PGPASSWORD="${PGPASSWORD:-}" pg_dump \
  --host="$PGHOST" \
  --port="$PGPORT" \
  --username="$PGUSER" \
  --dbname="$PGDATABASE" \
  --format=custom \
  --compress=9 \
  --no-password \
  --file="$BACKUP_FILE"

DUMP_SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
echo "[INFO] Backup complete — ${DUMP_SIZE} written to ${BACKUP_FILE}"

# ── Rotation ──────────────────────────────────────────────────────────────────
echo "[INFO] Pruning backups older than ${RETAIN_DAYS} days..."
find "$BACKUP_DIR" -name "yarnloop_*.dump" -mtime +"$RETAIN_DAYS" -print -delete

echo "[INFO] $(date -u +"%Y-%m-%dT%H:%M:%SZ") — Done."