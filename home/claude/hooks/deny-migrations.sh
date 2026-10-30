#!/usr/bin/env bash
# PreToolUse hook: deny the Write tool on framework migration files.
# Write is never allowed for migrations — generate new files with the framework CLI
# (drizzle-kit generate, php artisan make:migration, etc.) and modify existing ones
# with the Edit/Update tool only.
# Covers Laravel, Drizzle, Rails, Prisma, Alembic, Django, TypeORM, Knex, generic.

set -u

input="$(cat)"

file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"

if [ -z "$file_path" ]; then
  exit 0
fi
# Match common migration paths:
#   **/database/migrations/*  Laravel
#   **/db/migrate/*           Rails
#   **/prisma/migrations/*    Prisma
#   **/alembic/versions/*     Alembic / SQLAlchemy
#   **/drizzle/meta/*         Drizzle journal/snapshots
#   **/drizzle/<digit>...     Drizzle timestamped migration dirs
#   **/migrations/<digit>...  Django, TypeORM, Knex, generic
if printf '%s' "$file_path" | grep -qE '(^|/)(database/migrations|db/migrate|prisma/migrations|alembic/versions)/|(^|/)drizzle/(meta/|[0-9])|(^|/)migrations/[0-9][^/]*\.(ts|js|sql|py|rb)$'; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"The Write tool is not allowed for migration files (~/.claude/hooks/deny-migrations.sh). Generate new migrations with the framework CLI (drizzle-kit generate, php artisan make:migration, rails g migration, prisma migrate dev --create-only, alembic revision) and modify existing ones with the Edit tool only."}}
JSON
  exit 0
fi

exit 0
