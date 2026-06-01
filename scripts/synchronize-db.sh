#!/usr/bin/env bash
# Crontab entry (every day at 1:00 AM):
#   0 1 * * * /path/to/command-center/scripts/synchronize-db.sh >> /var/log/synchronize-db.log 2>&1
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
set -a
source "${SCRIPT_DIR}/../.env"
set +a

REMOTE="sims3-prod:/data/backups"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USERNAME:-root}"
DB_PASS="${DB_PASSWORD:-}"
DB_NAME="${DB_DATABASE_SIMS3:-sims3}"

MYSQL_OPTS="-h${DB_HOST} -P${DB_PORT} -u${DB_USER}"
if [ -n "$DB_PASS" ]; then
    MYSQL_OPTS="${MYSQL_OPTS} -p${DB_PASS}"
fi

TMPDIR="${TMPDIR:-/tmp}/synchronize-db"
mkdir -p "$TMPDIR"

LATEST=$(rclone ls "$REMOTE" | awk '{print $2}' | grep '\.sql\.gz$' | sort | tail -1)

if [ -z "$LATEST" ]; then
    echo "ERROR: No backup files found on remote." >&2
    exit 1
fi

echo "Latest backup: $LATEST"

BACKUP_FILE="$TMPDIR/$LATEST"
SQL_FILE="${BACKUP_FILE%.gz}"

echo "Downloading..."
rclone copyto "${REMOTE}/${LATEST}" "$BACKUP_FILE"

echo "Extracting..."
gunzip -f "$BACKUP_FILE"

echo "Recreating local database..."
mysql $MYSQL_OPTS -e "DROP DATABASE IF EXISTS \`${DB_NAME}\`; CREATE DATABASE \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo "Importing..."
mysql $MYSQL_OPTS "$DB_NAME" < "$SQL_FILE"

echo "Deleting production Telegram groups"
mysql $MYSQL_OPTS -e "USE \`${DB_NAME}\`; DELETE FROM telegram_groups WHERE id>1; UPDATE telegram_groups SET id=5049756594;"

echo "Cleaning up..."
rm -f "$BACKUP_FILE" "$SQL_FILE"

echo "Refreshing local database and recomputing KPIs..."
cd "$SCRIPT_DIR/.."
php artisan migrate:fresh --seed --force && php artisan compute:all

echo "Done."
